import random
import re
import time
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Generic, Iterator, TypeVar

import polars as pl
from curl_cffi import requests
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from pybaseballstats.consts.bref_consts import BREF_TEAM_CODE_SWITCHES, BREFTeams

# https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
T = TypeVar("T")


class Singleton(Generic[T]):
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated: type[T]) -> None:
        self._decorated = decorated
        self._instance: T | None = None

    def instance(self) -> T:
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        if self._instance is None:
            self._instance = self._decorated()
        return self._instance

    def __call__(self) -> None:
        raise TypeError("Singletons must be accessed through `instance()`.")

    def __instancecheck__(self, inst: object) -> bool:
        return isinstance(inst, self._decorated)


# https://github.com/jldbc/pybaseball/blob/master/pybaseball/datasources/bref.py
@Singleton
class BREFSession:
    """
    A singleton class to manage both requests and Selenium driver instances with rate limiting.
    """

    def __init__(
        self,
        max_req_per_minute=5,  # requests allowed per minute is 10 but we use 5 to be safe and account for retries
    ) -> None:
        self.max_req_per_minute: int = max_req_per_minute
        self.request_timestamps: deque[datetime] = deque(maxlen=max_req_per_minute)
        self.session: requests.Session = requests.Session()
        # Playwright browser management
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._lock = Lock()
        # Set common headers to appear more browser-like
        self.session.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    def _rate_limit(self) -> None:
        """Block until it's safe to make another request."""
        with self._lock:
            current_time = datetime.now()
            window_start = current_time - timedelta(minutes=1)

            # loop to remove timestamps older than 1 minute
            while self.request_timestamps and self.request_timestamps[0] < window_start:
                self.request_timestamps.popleft()

            if len(self.request_timestamps) >= self.max_req_per_minute:
                oldest_request_time = self.request_timestamps[0]
                wait_time = 60 - (current_time - oldest_request_time).total_seconds()
                wait_time = max(wait_time, 0)
                if wait_time > 0:
                    print(f"Rate limit reached, sleeping {wait_time:.2f}s")
                    time.sleep(
                        wait_time + random.uniform(0.5, 1.5)
                    )  # add a bit of jitter
                # After sleeping, update current_time and clean up old timestamps again

                current_time = datetime.now()
                window_start = current_time - timedelta(minutes=1)
                while (
                    self.request_timestamps
                    and self.request_timestamps[0] < window_start
                ):
                    self.request_timestamps.popleft()
            self.request_timestamps.append(current_time)

    def get(self, url: str, **kwargs: Any) -> requests.Response | None:
        """Make an HTTP request with rate limiting."""
        # call rate limit before making the request
        self._rate_limit()
        try:
            # Add Referer header if not present
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            if "Referer" not in kwargs["headers"]:
                kwargs["headers"]["Referer"] = "https://www.baseball-reference.com/"
            resp = self.session.get(url, impersonate="chrome", **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # error for too many requests
                print(
                    f"Received 429 Too Many Requests for {url}. Consider increasing the delay between requests."
                )
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def _ensure_browser_initialized(self) -> None:
        """Initialize browser if not already done."""
        if self._browser is None or not self._browser.is_connected():
            if self._browser:
                self._cleanup_browser()

            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = context.new_page()
            page.set_default_navigation_timeout(30000)
            page.set_default_timeout(20000)

            self._playwright = playwright
            self._browser = browser
            self._context = context
            self._page = page

    def _cleanup_browser(self) -> None:
        """Clean up browser resources."""
        if self._page:
            self._page.close()
            self._page = None
        if self._context:
            self._context.close()
            self._context = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    @contextmanager
    def get_page(self) -> Iterator[Page]:
        """Context manager for Playwright page with rate limiting."""
        self._rate_limit()

        with self._lock:
            try:
                self._ensure_browser_initialized()
                if self._page is None:
                    raise RuntimeError("Failed to initialize Playwright page")
                yield self._page
            except Exception as e:
                print(f"Browser error occurred: {e}")
                # Try to reinitialize browser on error
                self._cleanup_browser()
                raise

    def close_browser(self) -> None:
        """Manually close the browser session."""
        with self._lock:
            self._cleanup_browser()

    def __del__(self):
        """Cleanup when the singleton is destroyed."""
        self._cleanup_browser()


_INT_PATTERN = re.compile(r"^[+-]?\d+$")
_FLOAT_PATTERN = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?$")
_PERCENT_PATTERN = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?%$")


def _safe_parse_cell_value(value: str | None) -> str | int | float | None:
    """Parse a table cell value into int/float/string/None when safe.

    - Handles thousands separators in numeric strings (for example ``"12,345"``).
    - Handles percentages (for example ``"12.3%"`` and ``"-4%"``) as numeric values
      without the percent sign.
    - Preserves non-numeric content as strings.
    """
    if value is None:
        return None

    text = value.strip()
    if text == "":
        return None

    normalized = text.replace("−", "-")

    # Common non-values used in tables.
    if normalized in {"-", "--", "—", "N/A", "n/a", "NA", "na", "null", "NULL"}:
        return None

    # Accounting style negatives, e.g. "(1.2)" -> -1.2
    is_accounting_negative = normalized.startswith("(") and normalized.endswith(")")
    if is_accounting_negative:
        normalized = f"-{normalized[1:-1].strip()}"

    numeric_candidate = normalized.replace(",", "")

    if _PERCENT_PATTERN.match(numeric_candidate):
        try:
            return float(numeric_candidate[:-1])
        except ValueError:
            return text

    if _INT_PATTERN.match(numeric_candidate):
        try:
            return int(numeric_candidate)
        except ValueError:
            return text

    if _FLOAT_PATTERN.match(numeric_candidate):
        try:
            return float(numeric_candidate)
        except ValueError:
            return text

    return text


def _infer_series_dtype(values: list[str | int | float | None]) -> Any:
    """Infer a stable Polars dtype for parsed values."""
    non_null_values = [value for value in values if value is not None]
    if not non_null_values:
        return pl.Utf8

    if all(isinstance(value, int) for value in non_null_values):
        return pl.Int32

    if all(isinstance(value, (int, float)) for value in non_null_values):
        return pl.Float32

    return pl.Utf8


def _extract_table(table):
    """Extracts data from an HTML table into a dictionary of lists.

    Works specifically for Baseball Reference Tables
    """
    trs = table.tbody.find_all("tr")
    row_data: dict[str, list[str | int | float | None]] = {}
    for tr in trs:
        if tr.has_attr("class") and "thead" in tr["class"]:
            continue
        tds = tr.find_all("th")
        tds.extend(tr.find_all("td"))
        if len(tds) == 0:
            continue
        for td in tds:
            data_stat = td.attrs["data-stat"]
            if data_stat not in row_data:
                row_data[data_stat] = []
            if td.find("a") and data_stat != "player":  # special case for bref_draft
                raw_value = td.find("a").text
            elif td.find("a") and data_stat == "player":
                raw_value = td.text
            elif td.find("span"):
                raw_value = td.find("span").string
            elif td.find("strong"):
                raw_value = td.find("strong").string
            elif (
                data_stat == "homeORvis"
            ):  # special case for schedule/results table to determine home vs away
                if td.text.strip() == "@":
                    row_data[data_stat].append("away")
                else:
                    row_data[data_stat].append("home")
                continue
            else:
                raw_value = td.string

            row_data[data_stat].append(_safe_parse_cell_value(raw_value))

    typed_row_data: dict[str, pl.Series] = {}
    for column_name, values in row_data.items():
        dtype = _infer_series_dtype(values)
        if dtype == pl.Utf8:
            normalized_values: list[str | None] = [
                None if value is None else str(value) for value in values
            ]
            typed_row_data[column_name] = pl.Series(
                column_name, normalized_values, dtype=dtype
            )
        else:
            typed_row_data[column_name] = pl.Series(column_name, values, dtype=dtype)

    return typed_row_data


def resolve_bref_team_code(team: BREFTeams, year: int) -> str:
    """Resolve the Baseball Reference team code for a franchise/year.

    Args:
        team (BREFTeams): Stable franchise enum value.
        year (int): Season year.

    Raises:
        ValueError: If no code mapping is available for ``team``/``year``.

    Returns:
        str: Baseball Reference team code for URL usage.
    """
    ranges = BREF_TEAM_CODE_SWITCHES.get(team.value)
    if ranges is None:
        return team.value

    for start_year, end_year, team_code in ranges:
        if start_year <= year <= end_year:
            return team_code

    # If outside known bounds (e.g., a future year), use nearest known code.
    if year < ranges[0][0]:
        return ranges[0][2]
    if year > ranges[-1][1]:
        return ranges[-1][2]

    raise ValueError(
        f"No Baseball Reference team code mapping found for {team.name} in {year}."
    )
