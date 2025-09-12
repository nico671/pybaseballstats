import time
from datetime import datetime
from typing import Any, Optional

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
    A singleton class to manage the BREF instance.
    """

    def __init__(self, max_req_per_minute=10):
        self.max_req_per_minute = max_req_per_minute
        self.last_request_time: Optional[datetime] = None
        self.session = requests.Session()

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        if self.last_request_time:
            difference = datetime.now() - self.last_request_time
            wait_time = 60 / self.max_req_per_minute - difference.total_seconds()
            if wait_time > 0:
                time.sleep(wait_time)

        self.last_request_time = datetime.now()
        try:
            resp = self.session.get(url, impersonate="chrome", **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        return None


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
