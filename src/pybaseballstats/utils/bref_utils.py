import random
import re
import time
from collections import deque
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Generic, TypeVar

import polars as pl
from bs4 import BeautifulSoup, Comment
from curl_cffi import requests
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.sync_api import (
    sync_playwright,
)
from playwright_stealth import Stealth  # type: ignore[import-untyped]

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


@Singleton
class BREFSession:
    """
    A singleton class to manage requests, rate limiting, and automated
    Cloudflare bypassing via Playwright.
    """

    def __init__(
        self,
    ) -> None:
        self.max_req_per_minute: int = 5
        self.request_timestamps: deque[datetime] = deque(maxlen=5)

        # Initialize pure curl_cffi session with no manual headers
        self.session: requests.Session = requests.Session()

        self._lock = Lock()
        self.verbose = False

    def set_verbose(self, verbose: bool) -> None:
        """Enable or disable verbose logging for debugging."""
        self.verbose = verbose

    def _rate_limit(self) -> None:
        """Block until it's safe to make another request."""
        with self._lock:
            current_time = datetime.now()
            window_start = current_time - timedelta(minutes=1)

            # loop to remove timestamps older than 1 minute
            while self.request_timestamps and self.request_timestamps[0] < window_start:
                self.request_timestamps.popleft()
            # ensures no more than max_req_per_minute requests are made in any rolling 1-minute window
            if len(self.request_timestamps) >= self.max_req_per_minute:
                oldest_request_time = self.request_timestamps[0]
                wait_time = 60 - (current_time - oldest_request_time).total_seconds()
                wait_time = max(wait_time, 0)
                if wait_time > 0:
                    if self.verbose:
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
            # ensure it has been at least 3 seconds since the last request to avoid hitting Baseball References's rate limits
            if (
                self.request_timestamps
                and (current_time - self.request_timestamps[-1]).total_seconds() < 3
            ):
                wait_time = (
                    3 - (current_time - self.request_timestamps[-1]).total_seconds()
                )
                if self.verbose:
                    print(
                        f"Enforcing 3-second gap between requests, sleeping ~{wait_time:.2f}s"
                    )
                time.sleep(wait_time + random.uniform(0.5, 1.5))  # add a bit of jitter
            self.request_timestamps.append(current_time)

    def _is_cloudflare_challenge(self, response: requests.Response) -> bool:
        """Check if the response is a Cloudflare block/challenge."""
        if response.status_code in (403, 503):
            return True
        # Cloudflare challenges often return 200 but contain specific text
        text = response.text.lower()
        if (
            "just a moment" in text
            or "attention required" in text
            or "cloudflare" in text
        ):
            return True
        return False

    def _solve_cloudflare_challenge(self, url: str) -> None:
        """Spin up an ephemeral, stealthed Playwright instance to bypass Cloudflare."""
        if self.verbose:
            print(f"\n[DEBUG] === Initiating Cloudflare Bypass for {url} ===")

        import time

        try:
            with Stealth().use_sync(sync_playwright()) as p:
                if self.verbose:
                    print(
                        "[DEBUG] Launching visible browser with automation flags disabled..."
                    )
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-popup-blocking",
                    ],
                )

                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                )
                page = context.new_page()

                if self.verbose:
                    print("[DEBUG] Navigating to target URL...")
                page.goto(url, wait_until="domcontentloaded")

                start_time = time.time()
                max_wait = 45

                while time.time() - start_time < max_wait:
                    # 1. Victory Check
                    if page.locator("table, #footer").count() > 0:
                        if self.verbose:
                            print("\n[SUCCESS] Clearance achieved! Target page loaded.")
                        break

                    # 2. Element Scans
                    cf_iframes = page.frame_locator(
                        "iframe[src*='challenges'], iframe[src*='turnstile']"
                    )
                    shadow_turnstile = page.locator(
                        "input[name='cf-turnstile-response']"
                    )

                    iframe_count = page.locator(
                        "iframe[src*='challenges'], iframe[src*='turnstile']"
                    ).count()
                    shadow_count = shadow_turnstile.count()

                    if self.verbose:
                        print(
                            f"[DEBUG] Scan -> Iframes found: {iframe_count} | Hidden Shadow inputs found: {shadow_count}"
                        )

                    try:
                        target_x, target_y = None, None

                        # Scenario A: Closed Shadow DOM
                        if shadow_count > 0:
                            parent_div = shadow_turnstile.first.locator("..")
                            box = parent_div.bounding_box()
                            if self.verbose:
                                print(f"[DEBUG] Shadow DOM parent bounding box: {box}")

                            if box and box["width"] > 0:
                                target_x = box["x"] + 30 + random.uniform(-5, 5)
                                target_y = (
                                    box["y"]
                                    + (box["height"] / 2)
                                    + random.uniform(-5, 5)
                                )
                                if self.verbose:
                                    print(
                                        f"[DEBUG] Calculated Shadow Target: X={target_x:.1f}, Y={target_y:.1f}"
                                    )

                        # Scenario B: Standard iframe
                        elif iframe_count > 0:
                            checkbox = cf_iframes.locator(
                                ".cb-c, input[type='checkbox']"
                            ).first
                            if checkbox.is_visible(timeout=2000):
                                box = checkbox.bounding_box()
                                if self.verbose:
                                    print(
                                        f"[DEBUG] Standard Iframe checkbox bounding box: {box}"
                                    )
                                if box:
                                    target_x = (
                                        box["x"]
                                        + (box["width"] / 2)
                                        + random.uniform(-5, 5)
                                    )
                                    target_y = (
                                        box["y"]
                                        + (box["height"] / 2)
                                        + random.uniform(-5, 5)
                                    )
                                    if self.verbose:
                                        print(
                                            f"[DEBUG] Calculated Iframe Target: X={target_x:.1f}, Y={target_y:.1f}"
                                        )

                        # 3. Execution
                        if target_x is not None and target_y is not None:
                            if self.verbose:
                                print(
                                    "\n[ACTION] Target locked. Injecting visual debug dot..."
                                )

                            page.wait_for_timeout(random.randint(1000, 2000))

                            if self.verbose:
                                print("[ACTION] Moving mouse...")
                            page.mouse.move(
                                target_x, target_y, steps=random.randint(15, 30)
                            )
                            page.wait_for_timeout(random.randint(200, 500))

                            if self.verbose:
                                print("[ACTION] Clicking...")
                            page.mouse.down()
                            page.wait_for_timeout(random.randint(40, 120))
                            page.mouse.up()

                            page.mouse.move(
                                target_x + random.randint(100, 300),
                                target_y + random.randint(100, 300),
                                steps=random.randint(10, 20),
                            )

                            if self.verbose:
                                print(
                                    "[ACTION] Click complete. Waiting ~5 seconds for Cloudflare response...\n"
                                )
                            page.wait_for_timeout(5000 + random.randint(500, 1500))
                            continue

                    except Exception as e:
                        if self.verbose:
                            print(f"[DEBUG] Exception during targeting/clicking: {e}")

                    page.wait_for_timeout(1500)

                if page.locator("table, #footer").count() == 0:
                    if self.verbose:
                        print(
                            "\n[WARNING] Loop timed out. Saving debug screenshot to 'cf_timeout_debug.png'"
                        )
                if self.verbose:
                    print("[DEBUG] Extracting cookies...")
                for cookie in context.cookies():
                    self.session.cookies.set(
                        cookie["name"], cookie["value"], domain=cookie["domain"]
                    )
                if self.verbose:
                    print("[DEBUG] === Bypass Process Complete ===\n")

        except PlaywrightTimeoutError:
            print("\n[ERROR] Playwright timed out completely.")
        except Exception as e:
            print(f"\n[ERROR] Critical failure: {e}")

    def get(self, url: str, **kwargs: Any) -> requests.Response | None:
        """Make an HTTP request with automatic Waterfall escalation."""
        # _ensure_bref_enabled()
        self._rate_limit()

        try:
            # ATTEMPT 1: Fast curl_cffi
            resp = self.session.get(url, impersonate="chrome120", **kwargs)

            # Check for block
            if self._is_cloudflare_challenge(resp):
                # ATTEMPT 2: The Waterfall Escalation
                with self._lock:
                    self._solve_cloudflare_challenge(url)

                # Retry the fast request now that our session has the cf_clearance cookie
                self._rate_limit()
                resp = self.session.get(url, impersonate="chrome120", **kwargs)

            resp.raise_for_status()
            return resp

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Received 429 Too Many Requests for {url}. Backing off.")
            else:
                print(f"HTTP Error fetching {url}: {e}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")

        return None


def get_bref_table_html(html_content: str, table_id: str) -> str | None:
    """
    Extracts a specific table from Baseball Reference HTML.
    Checks the standard DOM first, then searches inside HTML comments
    for lazy-loaded tables.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Check if the table is normally rendered in the DOM
    target_table = soup.find("table", id=table_id)
    if target_table:
        return str(target_table)

    # 2. If not found, it is likely hidden inside an HTML comment
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if f'id="{table_id}"' in comment or f"id='{table_id}'" in comment:
            # Parse the hidden HTML
            hidden_soup = BeautifulSoup(comment, "html.parser")
            hidden_table = hidden_soup.find("table", id=table_id)
            if hidden_table:
                return str(hidden_table)

    print(f"Table with id '{table_id}' not found in DOM or comments.")
    return None


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
        used_data_stats: set[str] = set()
        for td in tds:
            data_stat = td.attrs["data-stat"]
            if data_stat in used_data_stats:
                continue
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
            used_data_stats.add(data_stat)
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
