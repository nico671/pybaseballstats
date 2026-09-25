import random
import time
from collections import deque
from threading import Lock
from typing import Any

from curl_cffi import requests
from playwright.sync_api import (
    Response as PlaywrightResponse,
)
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.sync_api import (
    sync_playwright,
)
from playwright_stealth import Stealth  # type: ignore[import-untyped]


class RateLimiter:
    """Reserve request times across callers in one process."""

    def __init__(self, max_req_per_minute: int | None = 5) -> None:
        if max_req_per_minute is not None and max_req_per_minute < 1:
            raise ValueError("max_req_per_minute must be positive or None")
        self.max_req_per_minute = max_req_per_minute
        self.request_timestamps: deque[float] = deque()
        self._lock = Lock()

    def wait(self, verbose: bool = False) -> None:
        if self.max_req_per_minute is None:
            return
        with self._lock:
            while True:
                now = time.monotonic()
                while (
                    self.request_timestamps and self.request_timestamps[0] <= now - 60
                ):
                    self.request_timestamps.popleft()

                minute_wait = (
                    max(0.0, 60 - (now - self.request_timestamps[0]))
                    if len(self.request_timestamps) >= self.max_req_per_minute
                    else 0.0
                )
                gap_wait = (
                    max(0.0, 5 - (now - self.request_timestamps[-1]))
                    if self.request_timestamps
                    else 0.0
                )
                wait_time = max(minute_wait, gap_wait)
                if wait_time == 0:
                    self.request_timestamps.append(now)
                    return
                if verbose:
                    print(f"Rate limit reached, sleeping {wait_time:.2f}s")
                time.sleep(wait_time + random.uniform(0.5, 1.5))


class PBSSessionManager:
    """Fetch pages with one session, rate limiter, and Cloudflare fallback."""

    def __init__(self, max_req_per_minute: int | None = 5) -> None:
        self.rate_limiter = RateLimiter(max_req_per_minute)
        self.session: requests.Session = requests.Session()
        self._lock = Lock()

    def _is_cloudflare_challenge(self, response: requests.Response) -> bool:
        """Check if the response is a Cloudflare block/challenge."""
        if response.status_code in (403, 503):
            return True
        # Cloudflare challenges often return 200 but contain specific text
        text = response.text.lower()
        if "just a moment" in text or "attention required" in text:
            return True
        return False

    def _solve_cloudflare_challenge(
        self, url: str, verbose: bool
    ) -> requests.Response | None:
        """Spin up an ephemeral, stealthed Playwright instance to bypass Cloudflare."""
        if verbose:
            print(f"\n[DEBUG] === Initiating Cloudflare Bypass for {url} ===")

        try:
            with Stealth().use_sync(sync_playwright()) as p:
                if verbose:
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
                    # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.96 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                )
                page = context.new_page()
                page_statuses: list[int] = []

                def capture_status(response: PlaywrightResponse) -> None:
                    if (
                        response.request.is_navigation_request()
                        and response.frame == page.main_frame
                    ):
                        page_statuses.append(response.status)

                page.on("response", capture_status)

                if verbose:
                    print("[DEBUG] Navigating to target URL...")
                page.goto(url, wait_until="domcontentloaded")

                max_clicks = 3
                num_clicks = 0

                while num_clicks < max_clicks:
                    # 1. Victory Check
                    if page.locator("table, #footer").count() > 0:
                        if verbose:
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

                    if verbose:
                        print(
                            f"[DEBUG] Scan -> Iframes found: {iframe_count} | Hidden Shadow inputs found: {shadow_count}"
                        )

                    try:
                        target_x, target_y = None, None

                        # Scenario A: Closed Shadow DOM
                        if shadow_count > 0:
                            parent_div = shadow_turnstile.first.locator("..")
                            box = parent_div.bounding_box()
                            if verbose:
                                print(f"[DEBUG] Shadow DOM parent bounding box: {box}")

                            if box and box["width"] > 0:
                                target_x = box["x"] + 30 + random.uniform(-5, 5)
                                target_y = (
                                    box["y"]
                                    + (box["height"] / 2)
                                    + random.uniform(-5, 5)
                                )
                                if verbose:
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
                                if verbose:
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
                                    if verbose:
                                        print(
                                            f"[DEBUG] Calculated Iframe Target: X={target_x:.1f}, Y={target_y:.1f}"
                                        )

                        # 3. Execution
                        if target_x is not None and target_y is not None:
                            if verbose:
                                print(
                                    "\n[ACTION] Target locked. Simulating human-like mouse movement and click..."
                                )
                            page.wait_for_timeout(random.randint(1000, 2000))

                            if verbose:
                                print("[ACTION] Moving mouse...")
                            page.mouse.move(
                                target_x, target_y, steps=random.randint(15, 30)
                            )
                            page.wait_for_timeout(random.randint(200, 500))

                            if verbose:
                                print("[ACTION] Clicking...")
                            page.mouse.down()
                            page.wait_for_timeout(random.randint(40, 120))
                            page.mouse.up()
                            num_clicks += 1
                            page.mouse.move(
                                target_x + random.randint(100, 300),
                                target_y + random.randint(100, 300),
                                steps=random.randint(10, 20),
                            )

                            if verbose:
                                print(
                                    "[ACTION] Click complete. Waiting ~5 seconds for Cloudflare response...\n"
                                )
                            page.wait_for_timeout(5000 + random.randint(500, 1500))
                            continue

                    except Exception as e:
                        if verbose:
                            print(f"[DEBUG] Exception during targeting/clicking: {e}")

                    page.wait_for_timeout(1500)

                page_ready = page.locator("table, #footer").count() > 0
                if not page_ready:
                    print(
                        "Cloudflare bypass did not reach a Baseball Reference page: "
                        f"url={url}, final_url={page.url}, "
                        f"navigation_statuses={page_statuses}, clicks={num_clicks}, "
                        f"challenge_iframes={iframe_count}, "
                        f"turnstile_inputs={shadow_count}"
                    )
                else:
                    if verbose:
                        print("[DEBUG] Extracting cookies...")
                    for cookie in context.cookies():
                        self.session.cookies.set(
                            cookie["name"], cookie["value"], domain=cookie["domain"]
                        )
                    if verbose:
                        print("[DEBUG] === Bypass Process Complete ===\n")
                    if not page_statuses:
                        return None
                    page_status = page_statuses[-1]
                    response = requests.Response()
                    response.url = page.url
                    response.status_code = page_status
                    response.ok = 200 <= page_status < 400
                    response.content = page.content().encode("utf-8")
                    response.raise_for_status()
                    return response

        except PlaywrightTimeoutError:
            print("\n[ERROR] Playwright timed out completely.")
        except Exception as e:
            print(f"\n[ERROR] Critical failure: {e}")
        return None

    def get(
        self, url: str, *, verbose: bool = False, **kwargs: Any
    ) -> requests.Response | None:
        """Make an HTTP request with optional debug logs and Cloudflare escalation."""
        self.rate_limiter.wait(verbose)

        try:
            # ATTEMPT 1: Fast curl_cffi
            resp = self.session.get(url, impersonate="chrome120", **kwargs)

            # Check for block
            if self._is_cloudflare_challenge(resp):
                print(
                    "Cloudflare challenge detected: "
                    f"url={url}, status={resp.status_code}, response_url={resp.url}"
                )
                # ATTEMPT 2: The Waterfall Escalation
                self.rate_limiter.wait(verbose)
                with self._lock:
                    return self._solve_cloudflare_challenge(url, verbose)

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


BREF_SESSION = PBSSessionManager(max_req_per_minute=5)
