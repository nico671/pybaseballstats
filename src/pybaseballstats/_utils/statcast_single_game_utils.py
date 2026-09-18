import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from playwright.async_api import async_playwright


@asynccontextmanager
async def get_page_async():
    """Async context manager for Playwright page."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
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

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        # Block unnecessary resources
        await context.route(
            "**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf,css}",
            lambda route: route.abort(),
        )

        page = await context.new_page()
        page.set_default_navigation_timeout(30000)
        page.set_default_timeout(15000)

        try:
            yield page
        finally:
            await page.close()
            await context.close()
            await browser.close()


def _handle_single_game_date(game_date: str):
    try:
        dt_object = datetime.strptime(game_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Incorrect date format. Please use YYYY-MM-DD format.")
    formatted_date = f"{dt_object.month}/{dt_object.day}/{dt_object.year}"
    return formatted_date.replace("/", "%2F")


async def fetch_gamefeed_table_html(
    page,
    url: str,
    selector: str,
    *,
    attempts: int = 3,
    navigation_timeout_ms: int = 90000,
    selector_timeout_ms: int = 30000,
) -> str:
    """Load a gamefeed page and return inner HTML for a table wrapper selector.

    This helper is resilient to intermittent network slowness in CI by retrying
    navigation and waiting for DOM readiness + target selector visibility.
    """
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            await page.goto(
                url,
                timeout=navigation_timeout_ms,
                wait_until="domcontentloaded",
            )
            await page.wait_for_selector(selector, timeout=selector_timeout_ms)
            html = await page.locator(selector).inner_html()
            if html:
                return html
            raise ValueError(f"Empty HTML for selector: {selector}")
        except Exception as exc:  # pragma: no cover - behavior tested via callers
            last_error = exc
            if attempt < attempts:
                await asyncio.sleep(0.75 * attempt)
                continue
            break

    assert last_error is not None
    raise RuntimeError(
        f"Failed to load selector '{selector}' from gamefeed URL after {attempts} attempts"
    ) from last_error
