import asyncio
from contextlib import contextmanager
from datetime import date, timedelta
from typing import Iterator, Tuple

import aiohttp
import dateparser
import polars as pl
from playwright.sync_api import sync_playwright
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn

from pybaseballstats.consts.statcast_consts import (
    STATCAST_YEAR_RANGES,
)


# region statcast_single_game helpers
@contextmanager
def get_page():
    """Context manager for Playwright page without rate limiting for statcast."""
    # Always create a fresh browser/context for each call
    playwright = sync_playwright().start()
    browser = None
    context = None
    page = None

    try:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--disable-logging",
                "--memory-pressure-off",
            ],
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        # Block unnecessary resources for faster loading
        context.route(
            "**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf,css}",
            lambda route: route.abort(),
        )

        page = context.new_page()
        page.set_default_navigation_timeout(30000)
        page.set_default_timeout(15000)

        yield page

    finally:
        # Always cleanup in reverse order
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()
        playwright.stop()


@contextmanager
def get_driver():
    """Legacy function that now uses Playwright instead of Selenium."""
    with get_page() as page:
        yield page


# endregion statcast_single_game helpers


# region statcast_date_range helpers
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


def _load_all_data(responses):
    data_list = []
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
        start_dt = dateparser.parse(start_date_str)
        end_dt = dateparser.parse(end_date_str)
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


# endregion statcast_date_range helpers
