import asyncio
import io
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterator, List, Optional, Tuple

import aiohttp
import polars as pl
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn

from pybaseballstats.consts.statcast_consts import (
    STATCAST_YEAR_RANGES,
)


@dataclass
class ChunkFetchResult:
    url: str
    dataframe: Optional[pl.DataFrame]
    error: Optional[str] = None


async def _fetch_and_parse_chunk(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3,
) -> ChunkFetchResult:
    async with semaphore:
        last_error = "Unknown error"

        for attempt in range(1, max_retries + 1):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
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
                                ignore_errors=True,
                                infer_schema_length=10000,
                            )
                            if df.height > 0:
                                return ChunkFetchResult(url=url, dataframe=df)
                            elif df.height == 0:
                                return ChunkFetchResult(
                                    url=url, dataframe=pl.DataFrame(), error=None
                                )

                            last_error = "Parsed CSV contained zero rows"
                            if attempt < max_retries:
                                await asyncio.sleep(1 * attempt)
                                continue
                            return ChunkFetchResult(
                                url=url, dataframe=None, error=last_error
                            )
                        except Exception as e:
                            # Sometimes empty or malformed CSVs come back
                            last_error = f"CSV parse error: {type(e).__name__}: {e}"
                            if attempt < max_retries:
                                await asyncio.sleep(1 * attempt)
                                continue
                            return ChunkFetchResult(
                                url=url, dataframe=None, error=last_error
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

            except Exception as e:
                # Retry all transport/runtime errors for data integrity guarantees.
                last_error = f"{type(e).__name__}: {e}"
                if attempt < max_retries:
                    await asyncio.sleep(1 * attempt)
                    continue
                return ChunkFetchResult(url=url, dataframe=None, error=last_error)

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
) -> List[pl.DataFrame]:
    """
    Orchestrates the fetching of all URLs.
    """
    # Tuning concurrency (caller may override).
    if concurrency is None:
        concurrency = 25 if date_range_total_days <= 30 else 15

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=15, sock_read=45)

    semaphore = asyncio.Semaphore(concurrency)
    results: List[pl.DataFrame] = []
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
        tasks = [_fetch_and_parse_chunk(session, url, semaphore) for url in urls]

        if show_progress:
            with Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task_id = progress.add_task("Downloading & Parsing...", total=len(urls))

                # as_completed yields futures as they finish, allowing us to update progress
                for future in asyncio.as_completed(tasks):
                    result = await future
                    if result.dataframe is not None:
                        results.append(result.dataframe)
                    else:
                        failed_chunks.append(result)
                    progress.update(task_id, advance=1)
        else:
            gathered = await asyncio.gather(*tasks)
            results.extend([r.dataframe for r in gathered if r.dataframe is not None])
            failed_chunks.extend([r for r in gathered if r.dataframe is None])

    if failed_chunks:
        failed_count = len(failed_chunks)
        sample_failures = failed_chunks[:5]
        details = "\n".join(
            f"  - {chunk.url} -> {chunk.error or 'Unknown error'}"
            for chunk in sample_failures
        )
        if failed_count > 5:
            details += f"\n  - ... and {failed_count - 5} more failed chunk(s)."

        raise RuntimeError(
            "Statcast download failed to retrieve all requested chunks after retries. "
            f"{failed_count}/{len(urls)} chunk(s) failed. "
            "Data integrity policy prevented returning partial data. "
            f"\nFailure details:\n{details}"
        )

    return results


def _load_all_data(
    responses: List[pl.DataFrame], *, show_progress: bool = True
) -> List[pl.LazyFrame]:
    """Convert fetched DataFrames into LazyFrames with a consistent schema.

    The download step returns parsed DataFrames for reliability. This function:
    - chooses a reference schema from the first successful chunk
    - aligns subsequent chunks to that schema (adds missing cols, drops extras, casts)
    - returns LazyFrames to preserve the public behavior of statcast.pitch_by_pitch_data
    """
    data_list: List[pl.LazyFrame] = []
    schema: dict[str, pl.DataType] | None = None
    schema_cols: List[str] = []

    def _align_df(df: pl.DataFrame) -> pl.DataFrame:
        assert schema is not None
        assert schema_cols

        # Add missing columns as nulls with the expected dtype
        missing = [c for c in schema_cols if c not in df.columns]
        if missing:
            df = df.with_columns(
                [pl.lit(None).cast(schema[c]).alias(c) for c in missing]
            )

        # Drop any unexpected columns
        extras = [c for c in df.columns if c not in schema]
        if extras:
            df = df.drop(extras)

        # Reorder and cast to match schema
        df = df.select(schema_cols)
        casts = []
        for c in schema_cols:
            try:
                current = df.schema.get(c)
                expected = schema[c]
                if current != expected:
                    casts.append(pl.col(c).cast(expected, strict=False))
            except Exception:
                # If schema lookup/cast fails for a column, keep it as-is.
                continue
        if casts:
            df = df.with_columns(casts)

        return df

    if show_progress:
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
            MofNCompleteColumn(),
        ) as progress:
            process_task = progress.add_task("Processing data...", total=len(responses))

            for response in responses:
                try:
                    if schema is None:
                        schema = dict(response.schema)
                        schema_cols = list(response.columns)
                        data_list.append(response.lazy())
                        continue

                    aligned = _align_df(response)
                    data_list.append(aligned.lazy())
                except Exception as e:
                    progress.log(f"Error processing data: {e}")
                    continue
                finally:
                    progress.update(process_task, advance=1)
    else:
        for response in responses:
            try:
                if schema is None:
                    schema = dict(response.schema)
                    schema_cols = list(response.columns)
                    data_list.append(response.lazy())
                    continue

                aligned = _align_df(response)
                data_list.append(aligned.lazy())
            except Exception:
                continue
    return data_list


def _handle_dates(start_date_str: str, end_date_str: str) -> Tuple[date, date]:
    """
    Helper function to handle date inputs.

    Args:
    start_dt: the start date in 'YYYY-MM-DD' format
    end_dt: the end date in 'YYYY-MM-DD' format

    Returns:
    A tuple of datetime.date objects for the start and end dates.
    """
    try:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing dates: {e}")
    assert start_dt is not None, "Could not parse start_date"
    assert end_dt is not None, "Could not parse end_date"
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
