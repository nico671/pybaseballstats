import time
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Optional

from curl_cffi import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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

    def __init__(self, max_req_per_minute=10) -> None:
        self.max_req_per_minute: int = max_req_per_minute
        self.request_timestamps: deque[datetime] = deque(maxlen=max_req_per_minute)
        self.session: requests.Session = requests.Session()
        self._driver: Optional[webdriver.Chrome] = None

    def _rate_limit(self) -> None:
        """
        Apply rate limiting to ensure no more than max_req_per_minute requests are made
        within any rolling 60-second window.
        """

        while True:
            current_time = datetime.now()
            # Remove timestamps older than 60 seconds
            window_start = current_time - timedelta(seconds=60)

            while self.request_timestamps and self.request_timestamps[0] < window_start:
                self.request_timestamps.popleft()

            # If we're under the limit, we can proceed
            if len(self.request_timestamps) < self.max_req_per_minute:
                break

            # Calculate time until the oldest request ages out of our 60-second window
            oldest_timestamp = self.request_timestamps[0]
            wait_time = 60 - (current_time - oldest_timestamp).total_seconds()

            if wait_time > 0:
                print(
                    f"Sleeping for {wait_time:.2f} seconds to avoid being rate limited"
                )
                time.sleep(wait_time)
            else:
                # This is a safety check in case of clock issues
                self.request_timestamps.popleft()

        # Add current time to our request timestamps
        self.request_timestamps.append(current_time)

    def get(self, url: str, **kwargs: Any) -> requests.Response | None:
        """Make an HTTP request with rate limiting."""
        self._rate_limit()
        try:
            resp = self.session.get(url, impersonate="chrome", **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def _create_driver(self) -> webdriver.Chrome:
        """Create a new Chrome driver with default options."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        )
        return webdriver.Chrome(options=options)

    @contextmanager
    def get_driver(self):
        """Context manager for getting a driver with rate limiting.
        Creates a new driver each time to prevent memory leaks."""
        self._rate_limit()
        driver = self._create_driver()
        try:
            yield driver
        finally:
            driver.quit()


def _extract_table(table):
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
