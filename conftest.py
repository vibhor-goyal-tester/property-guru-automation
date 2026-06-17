import pytest
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright

from playwright_config import HEADLESS, SLOW_MO, VIEWPORT, USER_AGENT, RETRIES
from pages.search_box_page import SearchBoxPage
from pages.more_filters_page import MoreFiltersPage
from pages.quick_filters_page import QuickFiltersPage
from utils.logger import get_logger

_log = get_logger(__name__)


@pytest.fixture(scope="session")
def browser_instance():
    """Single Chromium browser for the entire test session."""
    _log.info("Launching Chromium browser (headless=%s, slow_mo=%dms)", HEADLESS, SLOW_MO)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        _log.debug("Browser launched successfully")
        yield browser
        _log.info("Closing browser")
        browser.close()


@pytest.fixture()
def context(browser_instance: Browser):
    """Fresh browser context per test — cookies and storage are isolated."""
    _log.debug("Creating new browser context (viewport=%s)", VIEWPORT)
    ctx = browser_instance.new_context(
        viewport=VIEWPORT,
        user_agent=USER_AGENT,
        locale="en-SG",
        timezone_id="Asia/Singapore",
    )
    yield ctx
    _log.debug("Closing browser context")
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext):
    """Open a new tab for each test."""
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.fixture()
def js_errors(page: Page) -> list:
    """Collect JS console errors during a test for use with assert_no_js_errors()."""
    errors: list = []

    def _on_error(exc):
        _log.error("JS pageerror: %s", exc)
        errors.append(exc)

    page.on("pageerror", _on_error)
    return errors


@pytest.fixture()
def search_page(page: Page) -> SearchBoxPage:
    """Navigate to the listing page and return a ready SearchBoxPage."""
    _log.info("Setting up search_page fixture")
    sp = SearchBoxPage(page)
    sp.open()
    _log.info("search_page ready at: %s", page.url)
    return sp


@pytest.fixture()
def more_filters_page(page: Page) -> MoreFiltersPage:
    """Navigate to the listing page and return a ready MoreFiltersPage."""
    _log.info("Setting up more_filters_page fixture")
    mfp = MoreFiltersPage(page)
    mfp.open()
    _log.info("more_filters_page ready at: %s", page.url)
    return mfp


@pytest.fixture()
def quick_filters_page(page: Page) -> QuickFiltersPage:
    """Navigate to the listing page and return a ready QuickFiltersPage."""
    _log.info("Setting up quick_filters_page fixture")
    qfp = QuickFiltersPage(page)
    qfp.open()
    _log.info("quick_filters_page ready at: %s", page.url)
    return qfp


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "flaky: mark test as potentially flaky (will be retried)"
    )
