import time
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from playwright.sync_api import sync_playwright
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
class BREFSingleton:
    """
    A singleton class to manage the BREF instance.
    """

    def __init__(self, max_req_per_minute=10):
        self.max_req_per_minute = max_req_per_minute
        self.last_request_time: Optional[datetime] = None
        self.recent_requests = []  # List to track recent request timestamps
        self.driver_instance = None

    @contextmanager
    def get_driver(self):
        """
        Returns a WebDriver instance, but only if we haven't exceeded our rate limit.
        Uses a context manager pattern to ensure the driver is properly closed.

        Yields:
            webdriver.Chrome: A Chrome WebDriver instance

        Raises:
            RuntimeError: If the rate limit would be exceeded
        """
        # Check if we can make a request
        self.rate_limit_requests()

        # Create a new driver if needed
        if self.driver_instance is None:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver_instance = webdriver.Chrome(options=options)

        try:
            yield self.driver_instance
        finally:
            # We don't quit the driver here to allow reuse
            pass

    def quit_driver(self):
        """Explicitly quit the driver when done with all operations."""
        if self.driver_instance is not None:
            self.driver_instance.quit()
            self.driver_instance = None

    def rate_limit_requests(self):
        """
        Ensures that we don't exceed the maximum number of requests per minute.
        Waits if necessary before allowing a new request.

        Raises:
            RuntimeError: If rate limit would be exceeded even after waiting
        """
        now = datetime.now()

        # Remove timestamps older than 1 minute
        self.recent_requests = [
            t for t in self.recent_requests if (now - t).total_seconds() < 60
        ]

        # If we've reached the limit, wait until we can make another request
        if len(self.recent_requests) >= self.max_req_per_minute:
            oldest_request = min(self.recent_requests)
            seconds_to_wait = 60 - (now - oldest_request).total_seconds()

            if seconds_to_wait > 0:
                print(
                    f"Rate limit for Baseball Reference reached. Waiting for {seconds_to_wait:.2f} seconds before next request. Try to limit requests to Baseball Reference to {self.max_req_per_minute} per minute.",
                    f" Current requests in the last minute: {len(self.recent_requests)}",
                )
                time.sleep(seconds_to_wait)
        self.recent_requests.append(datetime.now())
        self.last_request_time = datetime.now()


# @contextmanager
# def get_driver():
#     """Provides a WebDriver instance that automatically quits on exit."""
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     driver = webdriver.Chrome(options=options)

#     try:
#         yield driver  # Hands control back to the calling function
#     finally:
#         driver.quit()  # Ensures WebDriver is always closed


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


def fetch_page_html(url: str) -> str:
    """
    Fetches the full HTML of a Baseball Reference page using Playwright
    (bypasses Cloudflare JavaScript challenge).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # Wait until network is idle (all JS/XHRs done)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
        return html
