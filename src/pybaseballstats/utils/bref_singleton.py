import time
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

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
