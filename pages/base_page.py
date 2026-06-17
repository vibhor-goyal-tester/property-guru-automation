import re

from playwright.sync_api import Page, expect
from playwright_config import BASE_URL, DEFAULT_TIMEOUT
from utils.logger import get_logger

_log = get_logger(__name__)


class BasePage:
    """Shared behaviour for every page object in this suite."""

    # Extend this list if new cookie banner variants appear
    _COOKIE_BANNER_SELECTORS = [
        "button:has-text('Accept')",
        "button:has-text('Accept All')",
        "button:has-text('I Agree')",
        "button:has-text('OK')",
        "[data-testid='cookie-accept']",
        "#onetrust-accept-btn-handler",
        ".cookie-accept",
    ]

    def __init__(self, page: Page) -> None:
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT)

    def navigate(self, url: str = BASE_URL) -> None:
        _log.info("Navigating to: %s", url)
        self.page.goto(url, wait_until="domcontentloaded")
        _log.debug("Page loaded: %s", self.page.url)
        self._dismiss_cookie_banner()

    def reload(self) -> None:
        _log.info("Reloading page: %s", self.page.url)
        self.page.reload(wait_until="domcontentloaded")
        self._dismiss_cookie_banner()

    def _dismiss_cookie_banner(self, timeout: int = 4_000) -> None:
        """Click the first visible cookie-consent button; silent if none appears."""
        for selector in self._COOKIE_BANNER_SELECTORS:
            try:
                btn = self.page.locator(selector).first
                btn.wait_for(state="visible", timeout=timeout)
                btn.click()
                _log.info("Cookie banner dismissed with selector: %s", selector)
                return
            except Exception:
                continue
        _log.debug("No cookie banner detected")

    def assert_url_contains(self, fragment: str) -> None:
        expect(self.page).to_have_url(re.compile(f".*{re.escape(fragment)}.*"))

    def assert_page_title_contains(self, text: str) -> None:
        expect(self.page).to_have_title(re.compile(f".*{text}.*", re.IGNORECASE))

    def get_current_url(self) -> str:
        return self.page.url
