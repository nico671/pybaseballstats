import asyncio
import io
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, List, Optional, Tuple

import aiohttp
import polars as pl
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn

from pybaseballstats._consts.statcast_consts import (
    STATCAST_YEAR_RANGES,
)

_LAZY_SOURCE_DIRS: list[TemporaryDirectory] = []


def _retain_lazy_sources(source_dir: TemporaryDirectory) -> None:
    """Keep scanned CSV files alive while a returned LazyFrame may use them."""
    _LAZY_SOURCE_DIRS.append(source_dir)


@dataclass
class ChunkFetchResult:
    url: str
    dataframe: Optional[pl.DataFrame]
    error: Optional[str] = None
    source_path: Optional[Path] = None
    cause: Exception | None = None


def _validate_streamed_csv(path: Path) -> bool:
    """Parse every row without loading the full download into memory."""
    scan = pl.scan_csv(
        path,
        null_values=["null", "NULL", "NA"],
        infer_schema_length=10000,
    )
    if "game_date" not in scan.collect_schema():
        raise ValueError("Statcast CSV is missing game_date")
    if hasattr(scan, "collect_batches"):
        has_rows = False
        for batch in scan.collect_batches(chunk_size=8192):
            has_rows = has_rows or batch.height > 0
        return has_rows

    # Older supported Polars versions do not have LazyFrame.collect_batches.
    reader = pl.read_csv_batched(
        path,
        null_values=["null", "NULL", "NA"],
        infer_schema_length=10000,
    )
    has_rows = False
    while (batches := reader.next_batches(1)) is not None:
        has_rows = has_rows or any(batch.height > 0 for batch in batches)
    return has_rows


async def _fetch_and_parse_chunk(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3,
    output_path: Path | None = None,
) -> ChunkFetchResult:
    async with semaphore:
        last_error = "Unknown error"

        for attempt in range(1, max_retries + 1):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        if output_path is not None:
                            try:
                                size = 0
                                with output_path.open("wb") as output:
                                    async for block in response.content.iter_chunked(
                                        64 * 1024
                                    ):
                                        output.write(block)
                                        size += len(block)
                                if size:
                                    _validate_streamed_csv(output_path)
                                    return ChunkFetchResult(
                                        url=url,
                                        dataframe=None,
                                        source_path=output_path,
                                    )
                                last_error = "Empty response body"
                            except (OSError, pl.exceptions.PolarsError, ValueError):
                                output_path.unlink(missing_ok=True)
                                raise
                            if attempt < max_retries:
                                await asyncio.sleep(1 * attempt)
                                continue
                            return ChunkFetchResult(
                                url=url, dataframe=None, error=last_error
                            )

                        raw_bytes = await response.read()
                        if not raw_bytes:
                            last_error = "Empty response body"
                            if attempt < max_retries:
                                await asyncio.sleep(1 * attempt)
                                continue
                            return ChunkFetchResult(
                                url=url, dataframe=None, error=last_error
                            )
                        try:
                            df = pl.read_csv(
                                io.BytesIO(raw_bytes),
                                null_values=["null", "NULL", "NA"],
                                infer_schema_length=10000,
                            )
                            if "game_date" not in df.columns:
                                raise ValueError("Statcast CSV is missing game_date")
                            return ChunkFetchResult(url=url, dataframe=df)
                        except (pl.exceptions.PolarsError, ValueError) as e:
                            # Sometimes empty or malformed CSVs come back
                            last_error = f"CSV parse error: {type(e).__name__}: {e}"
                            if attempt < max_retries:
                                await asyncio.sleep(1 * attempt)
                                continue
                            return ChunkFetchResult(
                                url=url, dataframe=None, error=last_error, cause=e
                            )
                    # Handle Non-200
                    else:
                        # Retry all HTTP errors for data integrity guarantees.
                        last_error = f"HTTP {response.status}"
                        if attempt < max_retries:
                            await asyncio.sleep(1.5 * attempt)
                            continue
                        return ChunkFetchResult(
                            url=url, dataframe=None, error=last_error
                        )

            except (
                aiohttp.ClientError,
                asyncio.TimeoutError,
                pl.exceptions.PolarsError,
                ValueError,
            ) as e:
                # Retry only expected transport and source-parse failures.
                last_error = f"{type(e).__name__}: {e}"
                if attempt < max_retries:
                    await asyncio.sleep(1 * attempt)
                    continue
                return ChunkFetchResult(
                    url=url, dataframe=None, error=last_error, cause=e
                )
            except OSError as e:
                return ChunkFetchResult(
                    url=url,
                    dataframe=None,
                    error=f"{type(e).__name__}: {e}",
                    cause=e,
                )

        return ChunkFetchResult(
            url=url,
            dataframe=None,
            error=f"Failed after {max_retries} retries. Last error: {last_error}",
        )


async def _fetch_all_data(
    urls: List[str],
    date_range_total_days: int,
    *,
    concurrency: int | None = None,
    show_progress: bool = True,
    output_dir: Path | None = None,
) -> List[pl.DataFrame | Path]:
    """
    Orchestrates the fetching of all URLs.
    """
    # Tuning concurrency (caller may override).
    if concurrency is None:
        concurrency = 25 if date_range_total_days <= 30 else 15

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=15, sock_read=45)

    semaphore = asyncio.Semaphore(concurrency)
    results: List[pl.DataFrame | Path | None] = [None] * len(urls)
    failed_chunks: List[ChunkFetchResult] = []

    if show_progress:
        print(
            f"Starting download of {len(urls)} chunks with {concurrency} concurrent workers..."
        )

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={
            "User-Agent": "pybaseballstats (https://github.com/nico671/pybaseballstats)",
        },
    ) as session:

        async def _fetch_indexed(index: int, url: str) -> Tuple[int, ChunkFetchResult]:
            result = await _fetch_and_parse_chunk(
                session,
                url,
                semaphore,
                output_path=(output_dir / f"chunk-{index:06d}.csv")
                if output_dir is not None
                else None,
            )
            return index, result

        tasks = [_fetch_indexed(index, url) for index, url in enumerate(urls)]

        def _add_result(index: int, result: ChunkFetchResult) -> None:
            if result.source_path is not None:
                results[index] = result.source_path
            elif result.dataframe is not None:
                if output_dir is None or not result.dataframe.is_empty():
                    results[index] = result.dataframe
            else:
                failed_chunks.append(result)

        if show_progress:
            with Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task_id = progress.add_task(
                    "Downloading..." if output_dir else "Downloading & Parsing...",
                    total=len(urls),
                )

                # as_completed yields futures as they finish, allowing us to update progress
                for future in asyncio.as_completed(tasks):
                    index, result = await future
                    _add_result(index, result)
                    progress.update(task_id, advance=1)
        else:
            gathered = await asyncio.gather(*tasks)
            for index, result in gathered:
                _add_result(index, result)

    if failed_chunks:
        failed_count = len(failed_chunks)
        sample_failures = failed_chunks[:5]
        details = "\n".join(
            f"  - {chunk.url} -> {chunk.error or 'Unknown error'}"
            for chunk in sample_failures
        )
        if failed_count > 5:
            details += f"\n  - ... and {failed_count - 5} more failed chunk(s)."

        failure = RuntimeError(
            "Statcast download failed to retrieve all requested chunks after retries. "
            f"{failed_count}/{len(urls)} chunk(s) failed. "
            "Data integrity policy prevented returning partial data. "
            f"\nFailure details:\n{details}"
        )
        if failed_chunks[0].cause is not None:
            raise failure from failed_chunks[0].cause
        raise failure

    return [result for result in results if result is not None]


def _load_all_data(
    responses: List[pl.DataFrame | Path], *, show_progress: bool = True
) -> List[pl.LazyFrame]:
    """Join downloaded chunks while retaining columns across schema changes."""
    if not responses:
        return []
    try:
        if all(isinstance(response, Path) for response in responses):
            scans = [
                pl.scan_csv(
                    response,
                    null_values=["null", "NULL", "NA"],
                    infer_schema_length=10000,
                )
                for response in responses
                if isinstance(response, Path)
            ]
            non_empty = [
                scan for scan in scans if not scan.limit(1).collect().is_empty()
            ]
        elif all(isinstance(response, pl.DataFrame) for response in responses):
            scans = [
                response.lazy()
                for response in responses
                if isinstance(response, pl.DataFrame)
            ]
            non_empty = [
                response.lazy()
                for response in responses
                if isinstance(response, pl.DataFrame) and not response.is_empty()
            ]
        else:
            raise RuntimeError("Statcast download returned mixed chunk formats")
        if not non_empty:
            return [pl.concat(scans, how="diagonal_relaxed")]
        combined = pl.concat(non_empty, how="diagonal_relaxed")
        known = set(combined.collect_schema())
        missing = [
            name
            for scan in scans
            for name in scan.collect_schema()
            if name not in known
        ]
        if missing:
            combined = combined.with_columns(
                pl.lit(None).cast(pl.String).alias(name)
                for name in dict.fromkeys(missing)
            )
        return [combined]
    except pl.exceptions.PolarsError as exc:
        raise RuntimeError("Statcast chunk schemas could not be joined") from exc


def _handle_dates(start_date_str: str, end_date_str: str) -> Tuple[date, date]:
    """
    Helper function to handle date inputs.

    Args:
    start_dt: the start date in 'YYYY-MM-DD' format
    end_dt: the end date in 'YYYY-MM-DD' format

    Returns:
    A tuple of datetime.date objects for the start and end dates.
    """
    if not isinstance(start_date_str, str) or not isinstance(end_date_str, str):
        raise TypeError("start_date and end_date must be YYYY-MM-DD strings")
    try:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}") from e
    if (
        start_dt.strftime("%Y-%m-%d") != start_date_str
        or end_dt.strftime("%Y-%m-%d") != end_date_str
    ):
        raise ValueError("Dates must use YYYY-MM-DD format")
    start_dt_date = start_dt.date()
    end_dt_date = end_dt.date()
    if start_dt_date > end_dt_date:
        raise ValueError("Start date must be before end date.")
    return start_dt_date, end_dt_date


# this function comes from https://github.com/jldbc/pybaseball/blob/master/pybaseball/statcast.py
def _create_date_ranges(
    start: date, stop: date, step: int, verbose: bool = True
) -> Iterator[Tuple[date, date]]:
    """
    Iterate over dates. Skip the offseason dates. Returns a pair of dates for beginning and end of each segment.
    Range is inclusive of the stop date.
    If verbose is enabled, it will print a message if it skips offseason dates.
    This version is Statcast specific, relying on skipping predefined dates from STATCAST_VALID_DATES.
    """
    if start == stop:
        yield start, stop
        return
    low = start

    while low <= stop:
        date_span = low.replace(month=3, day=15), low.replace(month=11, day=15)
        season_start, season_end = STATCAST_YEAR_RANGES.get(low.year, date_span)
        if low < season_start:
            low = season_start
        elif low > season_end:
            low, _ = STATCAST_YEAR_RANGES.get(
                low.year + 1, (date(month=3, day=15, year=low.year + 1), None)
            )

        if low > stop:
            return
        high = min(low + timedelta(step - 1), stop)
        yield low, high
        low += timedelta(days=step)
