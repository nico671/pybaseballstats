import asyncio
from datetime import date, datetime, timedelta
from typing import Iterator, Tuple

import aiohttp
import dateparser
import pandas as pd
import polars as pl
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn

STATCAST_SINGLE_GAME_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
STATCAST_DATE_RANGE_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=pitcher&game_date_gt={start_date}&game_date_lt={end_date}&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&type=details#results"
STATCAST_YEAR_RANGES = {
    2022: (date(2022, 3, 17), date(2022, 11, 5)),
    2016: (date(2016, 4, 3), date(2016, 11, 2)),
    2019: (date(2019, 3, 20), date(2019, 10, 30)),
    2017: (date(2017, 4, 2), date(2017, 11, 1)),
    2023: (date(2023, 3, 15), date(2023, 11, 1)),
    2020: (date(2020, 7, 23), date(2020, 10, 27)),
    2018: (date(2018, 3, 29), date(2018, 10, 28)),
    2015: (date(2015, 4, 5), date(2015, 11, 1)),
    2024: (date(2024, 3, 15), date(2024, 10, 25)),
    2021: (date(2021, 3, 15), date(2021, 11, 2)),
    2025: (date(2025, 3, 18), datetime.now().date()),
}

STATCAST_DATE_FORMAT = "%Y-%m-%d"


async def _fetch_data(session, url, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Error {response.status} for {url}")
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
                        continue
                    else:
                        return None
        except aiohttp.ClientPayloadError as e:
            if attempt < retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
                print(
                    f"Retrying... {retries - attempt - 1} attempts left. Error: {str(e)}"
                )
                continue
            else:
                print(f"Failed to fetch data from {url}. Error: {str(e)}")
                return None

        except aiohttp.SocketTimeoutError as e:
            if attempt < retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
                print(
                    f"Socket timeout. Retrying... {retries - attempt - 1} attempts left."
                )
                continue
            else:
                print(f"Socket timeout error for {url}: {e}")
                return None
        except Exception as e:
            print(f"Unexpected error for {url}: {e}")
            return None


async def _fetch_all_data(urls, date_range_total_days):
    session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=60)

    if date_range_total_days <= 30:
        max_concurrent_requests = 20
    else:
        max_concurrent_requests = 15

    semaphore = asyncio.Semaphore(max_concurrent_requests)  # Limit concurrent requests

    async def _fetch_data_with_semaphore(session, url):
        async with semaphore:
            return await _fetch_data(session, url)

    async with aiohttp.ClientSession(
        timeout=session_timeout,
    ) as session:
        tasks = [
            asyncio.create_task(_fetch_data_with_semaphore(session, url))
            for url in urls
        ]
        results = []

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
        ) as progress:
            ptask = progress.add_task("Fetching data...", total=len(tasks))
            for task in asyncio.as_completed(tasks):
                result = await task
                results.append(result)
                progress.update(ptask, advance=1)

        valid_results = [r for r in results if r is not None]

        if len(valid_results) < len(urls):
            print(
                f"Warning: {len(urls) - len(valid_results)} of {len(urls)} requests failed"
            )

        return valid_results


async def _statcast_date_range_helper(
    start_date: str,
    end_date: str,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_date is None or end_date is None:
        raise ValueError("start_date and end_date must be provided")
    start_dt, end_dt = _handle_dates(start_date, end_date)
    print(f"Pulling data for date range: {start_dt} to {end_dt}.")
    print("Splitting date range into smaller chunks.")
    date_ranges = list(_create_date_ranges(start_dt, end_dt, step=3))
    assert len(date_ranges) > 0, "No date ranges generated. Check your input dates."
    data_list = []

    urls = []
    for start_dt, end_dt in date_ranges:
        urls.append(
            STATCAST_DATE_RANGE_URL.format(
                start_date=start_dt,
                end_date=end_dt,
            )
        )
    date_range_total_days = (end_dt - start_dt).days
    responses = await _fetch_all_data(urls, date_range_total_days)
    schema = None
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        MofNCompleteColumn(),
    ) as progress:
        process_task = progress.add_task("Processing data...", total=len(responses))

        for i, response in enumerate(responses):
            try:
                if not schema:
                    df = pl.scan_csv(response)
                    data_list.append(df)
                    schema = df.collect_schema()
                else:
                    df = pl.scan_csv(response, schema=schema)
                    data_list.append(df)
            except Exception as e:
                progress.log(f"Error processing data: {e}")
                continue
            finally:
                progress.update(process_task, advance=1)
    if not data_list:
        print("No data was successfully retrieved.")
        return pl.LazyFrame() if not return_pandas else pd.DataFrame()

    elif len(data_list) > 0:
        print("Concatenating data.")
        df = pl.concat(data_list)
        return df if not return_pandas else df.collect().to_pandas()
    else:
        print("No data frames to concatenate.")
        return pl.LazyFrame() if not return_pandas else pd.DataFrame()


def _handle_dates(start_dt: str, end_dt: str) -> Tuple[date, date]:
    """
    Helper function to handle date inputs.

    Args:
    start_dt: the start date in 'YYYY-MM-DD' format
    end_dt: the end date in 'YYYY-MM-DD' format

    Returns:
    A tuple of datetime.date objects for the start and end dates.
    """
    try:
        start_dt_date = dateparser.parse(start_dt).date()
        end_dt_date = dateparser.parse(end_dt).date()
    except ValueError:
        raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")
    if start_dt_date > end_dt_date:
        raise ValueError("start_dt must be before end_")
    return start_dt_date, end_dt_date


# this function comes from https://github.com/jldbc/pybaseball/blob/master/pybaseball/statcast.py
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
