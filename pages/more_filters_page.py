from playwright.sync_api import Page, Locator, TimeoutError as PWTimeoutError, expect

from pages.base_page import BasePage
from utils.helpers import is_visible, wait_for_search_response
from utils.logger import get_logger

_log = get_logger(__name__)


class MoreFiltersPage(BasePage):
    """Page object for the More Filters accordion modal (Screen 2)."""

    _FILTERS_BTN = (
        "[da-id='more-filter-button'], "
        "button[icon='filter-1-o'], "
        "button[label='Filters']"
    )

    _MODAL = "[role='dialog'][aria-modal='true']"

    _CLOSE_BTN = (
        "[role='dialog'] .btn-close, "
        "[role='dialog'] button[aria-label*='lose'], "
        "[role='dialog'] .modal-header button"
    )

    _APPLY_BTN = "[role='dialog'] button:has-text('Apply')"
    _CLEAR_BTN = "[role='dialog'] button:has-text('Clear')"

    _LISTING_CARD = (
        "[da-id='parent-listing-card-v2-regular'], "
        "[da-id^='parent-listing-card-v2']"
    )

    @property
    def modal(self) -> Locator:
        return self.page.locator(self._MODAL)

    @property
    def filters_button(self) -> Locator:
        return self.page.locator(self._FILTERS_BTN).first

    @property
    def apply_button(self) -> Locator:
        return self.modal.get_by_role("button", name="Apply")

    @property
    def clear_button(self) -> Locator:
        return self.modal.get_by_role("button", name="Clear")

    @property
    def close_button(self) -> Locator:
        return self.page.locator(self._CLOSE_BTN).first

    def _section(self, heading_text: str) -> Locator:
        """Return a locator scoped to the accordion section with `heading_text`."""
        return self.modal.locator(
            f"xpath=//h2[contains(., '{heading_text}')]/parent::*"
        )

    @property
    def property_type_group(self) -> Locator:
        return self._section("Property Type").get_by_role("group")

    @property
    def bedroom_group(self) -> Locator:
        return self._section("Bedroom").get_by_role("group")

    @property
    def price_min_input(self) -> Locator:
        return self._section("Price").get_by_role("spinbutton").first

    @property
    def price_max_input(self) -> Locator:
        return self._section("Price").get_by_role("spinbutton").last

    @property
    def floor_size_min_input(self) -> Locator:
        return self._section("Floor Size").get_by_role("spinbutton").first

    @property
    def floor_size_max_input(self) -> Locator:
        return self._section("Floor Size").get_by_role("spinbutton").last

    @property
    def listing_cards(self) -> Locator:
        return self.page.locator(self._LISTING_CARD)

    def open(self) -> None:
        _log.info("Opening MoreFiltersPage")
        self.navigate()
        self.page.locator(self._FILTERS_BTN).first.wait_for(state="visible", timeout=15_000)
        _log.debug("MoreFiltersPage ready at: %s", self.page.url)

    def open_modal(self) -> None:
        _log.info("Opening More Filters modal")
        self.filters_button.click()
        self.modal.wait_for(state="visible", timeout=10_000)
        _log.info("More Filters modal is open")

    def close_modal_via_button(self) -> None:
        _log.info("Closing More Filters modal via close button")
        self.close_button.click()
        self.modal.wait_for(state="hidden", timeout=5_000)

    def close_modal_via_escape(self) -> None:
        _log.info("Closing More Filters modal via Escape")
        self.page.keyboard.press("Escape")
        self.modal.wait_for(state="hidden", timeout=5_000)

    def is_modal_open(self) -> bool:
        return is_visible(self.modal, timeout=2_000)

    def select_property_type(self, prop_type: str) -> None:
        """Click the visible label chip; hidden radio updates state."""
        _log.info("Selecting property type: %r", prop_type)
        self.property_type_group.locator("label", has_text=prop_type).click()

    def get_selected_property_type(self) -> str:
        for label in self.property_type_group.get_by_role("radio").all():
            if label.is_checked():
                return label.get_attribute("value") or label.inner_text()
        return ""

    def select_bedroom(self, *bedrooms: str) -> None:
        """Click the visible label chips; hidden checkboxes update state."""
        for bedroom in bedrooms:
            _log.info("Selecting bedroom: %r", bedroom)
            self.bedroom_group.locator("label", has_text=bedroom).click()

    def deselect_bedroom(self, *bedrooms: str) -> None:
        for bedroom in bedrooms:
            _log.info("Deselecting bedroom: %r", bedroom)
            self.bedroom_group.locator("label", has_text=bedroom).click()

    def get_selected_bedrooms(self) -> list[str]:
        selected = []
        for cb in self.bedroom_group.get_by_role("checkbox").all():
            if cb.is_checked():
                selected.append(cb.get_attribute("value") or cb.inner_text())
        _log.debug("Selected bedrooms: %s", selected)
        return selected

    def set_price_range(
        self,
        min_price: int | None = None,
        max_price: int | None = None,
    ) -> None:
        if min_price is not None:
            _log.info("Setting min price: %d", min_price)
            self.price_min_input.fill(str(min_price))
        if max_price is not None:
            _log.info("Setting max price: %d", max_price)
            self.price_max_input.fill(str(max_price))

    def get_price_range(self) -> tuple[str, str]:
        return (
            self.price_min_input.input_value(),
            self.price_max_input.input_value(),
        )

    def set_floor_size_range(
        self,
        min_sqft: int | None = None,
        max_sqft: int | None = None,
    ) -> None:
        if min_sqft is not None:
            _log.info("Setting min floor size: %d sqft", min_sqft)
            self.floor_size_min_input.fill(str(min_sqft))
        if max_sqft is not None:
            _log.info("Setting max floor size: %d sqft", max_sqft)
            self.floor_size_max_input.fill(str(max_sqft))

    def apply_filters(self) -> None:
        _log.info("Applying filters")
        wait_for_search_response(self.page, action=self.apply_button.click)
        try:
            self.modal.wait_for(state="hidden", timeout=5_000)
            _log.debug("Modal closed after Apply")
        except PWTimeoutError:
            _log.warning("Modal did not close after Apply — may still be open")
        _log.info("Filters applied")

    def clear_filters(self) -> None:
        _log.info("Clearing all filters in modal")
        self.clear_button.click()

    def wait_for_results(self, timeout: int = 15_000) -> None:
        _log.debug("Waiting for results after filter (timeout=%dms)", timeout)
        self.listing_cards.first.wait_for(state="visible", timeout=timeout)
        count = self.listing_cards.count()
        _log.info("Results refreshed: %d listing card(s) visible", count)

    def get_listing_count(self) -> int:
        count = self.listing_cards.count()
        _log.debug("Listing count: %d", count)
        return count

    def is_apply_button_enabled(self) -> bool:
        return self.apply_button.is_enabled()
