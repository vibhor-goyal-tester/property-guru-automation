import re
import time
from typing import Callable, Optional

from playwright.sync_api import Page, Locator, TimeoutError as PWTimeoutError
from utils.logger import get_logger

_log = get_logger(__name__)


# Network helpers

def wait_for_search_response(page: Page, action: Callable, timeout: int = 15_000) -> None:
    """Execute `action` and wait for the search API response to settle."""
    api_patterns = [
        re.compile(r".*listing.*", re.I),
        re.compile(r".*search.*", re.I),
        re.compile(r".*property.*", re.I),
    ]

    try:
        _log.debug("Waiting for search API response (timeout=%dms)", timeout)
        with page.expect_response(
            lambda r: any(p.search(r.url) for p in api_patterns) and r.status == 200,
            timeout=timeout,
        ):
            action()
        _log.debug("Search API response received")
    except PWTimeoutError:
        _log.warning("No matching search XHR — falling back to DOM wait")
        action()
        page.wait_for_load_state("domcontentloaded", timeout=timeout)


def is_visible(locator: Locator, timeout: int = 3_000) -> bool:
    """Return True if the locator is visible within `timeout` ms."""
    try:
        locator.wait_for(state="visible", timeout=timeout)
        return True
    except PWTimeoutError:
        return False


def wait_for_any(page: Page, selectors: list[str], timeout: int = 10_000) -> Optional[str]:
    """
    Wait for the first selector in `selectors` to become visible.
    Returns the matching selector string, or None if all time out.
    """
    deadline = time.monotonic() + timeout / 1_000
    while time.monotonic() < deadline:
        for sel in selectors:
            if is_visible(page.locator(sel), timeout=500):
                return sel
        time.sleep(0.2)
    return None


def get_result_count(page: Page) -> Optional[int]:
    """Extract the total listing count from the results header, or None if not found."""
    count_selectors = [
        "[data-testid='listing-count']",
        ".listing-count",
        ".search-result-count",
        "h1",
        "h2",
        ".results-header",
    ]
    for sel in count_selectors:
        locator = page.locator(sel).first
        if is_visible(locator, timeout=2_000):
            text = locator.inner_text()
            numbers = re.findall(r"[\d,]+", text.replace(",", ""))
            if numbers:
                return int(max(numbers, key=lambda n: int(n)))
    return None


def page_contains_any(page: Page, texts: list[str]) -> bool:
    """Return True if any of `texts` appears (case-insensitive) in the page body."""
    body = page.locator("body").inner_text().lower()
    return any(t.lower() in body for t in texts)


# Known third-party/analytics errors that are unrelated to the app under test
_THIRD_PARTY_ERROR_PATTERNS = [
    "osdlfm", "googletag", "__cmp", "adsbygoogle", "fbq", "ttq", "clarity", "scorecard",
]


def _is_third_party_error(error) -> bool:
    msg = str(error).lower()
    return any(pat in msg for pat in _THIRD_PARTY_ERROR_PATTERNS)


def assert_no_js_errors(page: Page, errors: list) -> None:
    """Assert no application JS errors occurred; known third-party noise is ignored."""
    third_party, app_errors = [], []
    for err in errors:
        if _is_third_party_error(err):
            _log.warning("Ignoring known third-party JS error: %s", err)
            third_party.append(err)
        else:
            _log.error("JavaScript error detected: %s", err)
            app_errors.append(err)

    if not errors:
        _log.debug("No JavaScript errors detected")

    assert not app_errors, (
        f"JavaScript errors detected on page:\n"
        + "\n".join(str(e) for e in app_errors)
    )


def assert_no_crash(page: Page) -> None:
    """Assert the page did not navigate to an error page."""
    title = page.title().lower()
    url = page.url.lower()
    _log.debug("Checking for crash — title: %r, url: %s", title, url)
    assert "error" not in title, f"Page title indicates an error: {page.title()}"
    assert "/500" not in url, f"Server error URL detected: {page.url}"
    assert "404" not in url, f"Not-found URL detected: {page.url}"
    _log.debug("No crash detected")
