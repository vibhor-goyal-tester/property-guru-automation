from playwright.sync_api import Page, Locator, TimeoutError as PWTimeoutError, expect

from pages.base_page import BasePage
from utils.helpers import (
    wait_for_search_response,
    is_visible,
    wait_for_any,
    get_result_count,
)
from utils.logger import get_logger

_log = get_logger(__name__)


class SearchBoxPage(BasePage):
    """Page object for the Search Box on the PropertyGuru listing page (Screen 1)."""

    # Update selectors here if the UI changes — tests must never reference raw selectors.

    _SEARCH_INPUT = (
        "[da-id='search-box-input'], "
        "input[role='combobox'][placeholder*='Search'], "
        "input[placeholder='Search Location']"
    )

    # PropertyGuru has no dedicated Submit button; search is triggered by Enter
    _SEARCH_BUTTON = "[da-id='search-box-submit-DOES-NOT-EXIST']"

    # Autocomplete dropdown — a listbox with aria-label="menu-options"
    _AUTOCOMPLETE_CONTAINER = (
        "[aria-label='menu-options'], "
        "[role='listbox']"
    )

    # Excludes static "Search by MRT / District / Area / HDB Estate" header items
    _AUTOCOMPLETE_ITEM = "[role='option']:not(.search-options-item-root)"

    _LISTING_CARD = (
        "[da-id='parent-listing-card-v2-regular'], "
        "[da-id^='parent-listing-card-v2']"
    )

    _NO_RESULTS = (
        ".search-page-body--empty, "
        "[class*='search-page-body--empty']"
    )

    _CLEAR_BUTTON = (
        "[da-id='search-box-clear'], "
        ".search-typeahead__clear-button"
    )

    @property
    def search_input(self) -> Locator:
        return self.page.locator(self._SEARCH_INPUT).first

    @property
    def search_button(self) -> Locator:
        return self.page.locator(self._SEARCH_BUTTON).first

    @property
    def autocomplete_container(self) -> Locator:
        return self.page.locator(self._AUTOCOMPLETE_CONTAINER).first

    @property
    def autocomplete_items(self) -> Locator:
        return self.page.locator(self._AUTOCOMPLETE_ITEM)

    @property
    def listing_cards(self) -> Locator:
        return self.page.locator(self._LISTING_CARD)

    @property
    def no_results_banner(self) -> Locator:
        return self.page.locator(self._NO_RESULTS).first

    @property
    def clear_button(self) -> Locator:
        return self.page.locator(self._CLEAR_BUTTON).first

    def open(self) -> None:
        _log.info("Opening SearchBoxPage")
        self.navigate()
        self.wait_for_search_box()

    def wait_for_search_box(self, timeout: int = 15_000) -> None:
        self.search_input.wait_for(state="visible", timeout=timeout)

    def type_in_search(self, keyword: str) -> None:
        _log.info("Typing into search box: %r", keyword)
        self.search_input.click()
        self.search_input.fill(keyword)

    def type_char_by_char(self, keyword: str, delay: int = 80) -> None:
        """Type one character at a time to trigger keystroke-based autocomplete."""
        _log.info("Typing char-by-char: %r (delay=%dms)", keyword, delay)
        self.search_input.click()
        self.search_input.clear()
        self.search_input.type(keyword, delay=delay)

    def submit_search(self) -> None:
        """Submit by pressing Enter (PropertyGuru has no dedicated Search button)."""
        _log.info("Submitting search via Enter key")
        wait_for_search_response(
            self.page,
            action=lambda: self.search_input.press("Enter"),
        )

    def search(self, keyword: str, submit_via: str = "enter") -> None:
        _log.info("Searching for: %r", keyword)
        self.type_in_search(keyword)
        self.submit_search()

    def clear_search(self) -> None:
        if is_visible(self.clear_button, timeout=2_000):
            _log.info("Clearing search via clear button")
            self.clear_button.click()
        else:
            _log.info("Clear button not found — clearing via triple-click + Delete")
            self.search_input.triple_click()
            self.search_input.press("Delete")

    def wait_for_autocomplete(self, timeout: int = 5_000) -> bool:
        """Wait for location autocomplete suggestions (not the static focus options)."""
        _log.debug("Waiting for autocomplete suggestions (timeout=%dms)", timeout)
        appeared = is_visible(self.autocomplete_items.first, timeout=timeout)
        if not appeared:
            _log.warning("Autocomplete suggestions did not appear within %dms", timeout)
        return appeared

    def get_autocomplete_suggestions(self) -> list[str]:
        self.autocomplete_items.first.wait_for(state="visible", timeout=5_000)
        suggestions = self.autocomplete_items.all_inner_texts()
        _log.info("Autocomplete suggestions (%d): %s", len(suggestions), suggestions)
        return suggestions

    def select_autocomplete_suggestion(self, index: int = 0) -> None:
        _log.info("Selecting autocomplete suggestion at index %d", index)
        items = self.autocomplete_items
        items.nth(index).wait_for(state="visible", timeout=5_000)
        wait_for_search_response(
            self.page,
            action=lambda: items.nth(index).click(),
        )

    def wait_for_results(self, timeout: int = 15_000) -> None:
        self.listing_cards.first.wait_for(state="visible", timeout=timeout)
        count = self.listing_cards.count()
        _log.info("Results loaded: %d listing card(s) visible", count)

    def get_listing_count(self) -> int:
        count = self.listing_cards.count()
        _log.debug("Listing card count: %d", count)
        return count

    def get_result_count_from_header(self):
        return get_result_count(self.page)

    def is_no_results_shown(self) -> bool:
        visible = is_visible(self.no_results_banner, timeout=5_000)
        _log.debug("No-results banner visible: %s", visible)
        return visible

    def get_search_input_value(self) -> str:
        """Return the current value of the search input field."""
        return self.search_input.input_value()

    def get_input_max_length(self) -> int | None:
        """Return the maxlength attribute of the search input, or None if absent."""
        val = self.search_input.get_attribute("maxlength")
        return int(val) if val else None
