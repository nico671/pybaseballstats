import random
import time
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timedelta
from threading import Lock
from typing import Any

from curl_cffi import requests
from playwright.sync_api import sync_playwright


# https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
class Singleton:
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

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError("Singletons must be accessed through `instance()`.")

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


# https://github.com/jldbc/pybaseball/blob/master/pybaseball/datasources/bref.py
@Singleton
class BREFSession:
    """
    A singleton class to manage both requests and Selenium driver instances with rate limiting.
    """

    def __init__(
        self,
        max_req_per_minute=5,  # requests allowed per minute, technically 10 is the maximum but being conservative
    ) -> None:
        self.max_req_per_minute: int = max_req_per_minute
        self.request_timestamps: deque[datetime] = deque(maxlen=max_req_per_minute)
        self.session: requests.Session = requests.Session()

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

    @contextmanager
    def get_page(self):
        """Context manager for Playwright page with rate limiting."""
        self._rate_limit()

        playwright = sync_playwright().start()
        browser = None
        context = None
        page = None

        try:
            browser = playwright.chromium.launch(
                headless=True,
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )

            page = context.new_page()
            page.set_default_navigation_timeout(30000)
            page.set_default_timeout(20000)

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


def _extract_table(table):
    """Extracts data from an HTML table into a dictionary of lists.

    Works specifically for Baseball Reference Tables
    """
    trs = table.tbody.find_all("tr")
    row_data = {}
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
                row_data[data_stat].append(td.find("a").text)
            elif td.find("a") and data_stat == "player":
                row_data[data_stat].append(td.text)
            elif td.find("span"):
                row_data[data_stat].append(td.find("span").string)
            elif td.find("strong"):
                row_data[data_stat].append(td.find("strong").string)
            else:
                row_data[data_stat].append(td.string)
    return row_data
