from playwright.sync_api import Page, Locator, TimeoutError as PWTimeoutError, expect

from pages.base_page import BasePage
from utils.helpers import is_visible, wait_for_search_response
from utils.logger import get_logger

_log = get_logger(__name__)


class QuickFiltersPage(BasePage):
    """Page object for the Quick Filters tabbed modal (Screen 3)."""

    # Tabs: Property Type (radios), Price (spinbuttons), Bedroom (checkboxes)
    # If selectors break after a deploy, update only the constants below.

    _PROP_TYPE_TRIGGER = (
        "[da-id='quick-filter-property-type-search-root'], "
        "button:has-text('Property Type'):not([role='dialog'] *)"
    )
    _PRICE_TRIGGER = (
        "[da-id='quick-filter-price-search-root'], "
        "button:has-text('Price'):not([role='dialog'] *)"
    )
    _BEDROOM_TRIGGER = (
        "[da-id='quick-filter-bedrooms-root'], "
        "button:has-text('Bedroom'):not([role='dialog'] *)"
    )

    _MODAL = "[role='dialog'][aria-modal='true']"

    # Tabs are <a role="button">, not <button> tags
    _TAB_PROP_TYPE = "[role='dialog'] [role='button']:has-text('Property Type')"
    _TAB_PRICE     = "[role='dialog'] [role='button']:has-text('Price')"
    _TAB_BEDROOM   = "[role='dialog'] [role='button']:has-text('Bedroom')"

    # Inactive panes lack the 'active' class
    _TABPANEL = "[role='tabpanel'].active"

    _APPLY_BTN = "[role='dialog'] button:has-text('Apply')"
    _CLEAR_BTN  = "[role='dialog'] button:has-text('Clear')"

    _LISTING_CARD = (
        "[da-id='parent-listing-card-v2-regular'], "
        "[da-id^='parent-listing-card-v2']"
    )

    @property
    def modal(self) -> Locator:
        return self.page.locator(self._MODAL)

    @property
    def tabpanel(self) -> Locator:
        return self.modal.locator(self._TABPANEL)

    @property
    def apply_button(self) -> Locator:
        return self.modal.get_by_role("button", name="Apply")

    @property
    def clear_button(self) -> Locator:
        return self.modal.get_by_role("button", name="Clear")

    @property
    def listing_cards(self) -> Locator:
        return self.page.locator(self._LISTING_CARD)

    @property
    def property_type_group(self) -> Locator:
        return self.tabpanel.get_by_role("group")

    @property
    def price_min_input(self) -> Locator:
        return self.tabpanel.get_by_role("spinbutton").first

    @property
    def price_max_input(self) -> Locator:
        return self.tabpanel.get_by_role("spinbutton").last

    @property
    def bedroom_group(self) -> Locator:
        return self.tabpanel.get_by_role("group")

    def open(self) -> None:
        _log.info("Opening QuickFiltersPage")
        self.navigate()
        # Wait for at least one quick-filter trigger button
        self.page.locator(self._PROP_TYPE_TRIGGER).first.wait_for(
            state="visible", timeout=15_000
        )
        _log.debug("QuickFiltersPage ready at: %s", self.page.url)

    # ── Trigger methods

    def open_property_type_filter(self) -> None:
        """Click the Property Type button to open the modal on the Property Type tab."""
        _log.info("Opening Quick Filters via 'Property Type' trigger")
        self.page.locator(self._PROP_TYPE_TRIGGER).first.click()
        self.modal.wait_for(state="visible", timeout=10_000)
        _log.info("Quick Filters modal open on Property Type tab")

    def open_price_filter(self) -> None:
        """Click the Price button to open the modal on the Price tab."""
        _log.info("Opening Quick Filters via 'Price' trigger")
        self.page.locator(self._PRICE_TRIGGER).first.click()
        self.modal.wait_for(state="visible", timeout=10_000)
        _log.info("Quick Filters modal open on Price tab")

    def open_bedroom_filter(self) -> None:
        _log.info("Opening Quick Filters via 'Bedroom' trigger")
        self.page.locator(self._BEDROOM_TRIGGER).first.click()
        self.modal.wait_for(state="visible", timeout=10_000)
        _log.info("Quick Filters modal open on Bedroom tab")

    def switch_to_tab(self, tab_name: str) -> None:
        """Switch to the named tab ('Property Type', 'Price', or 'Bedroom')."""
        _log.info("Switching to tab: %r", tab_name)
        tab_selectors = {
            "Property Type": self._TAB_PROP_TYPE,
            "Price": self._TAB_PRICE,
            "Bedroom": self._TAB_BEDROOM,
        }
        selector = tab_selectors.get(tab_name)
        if not selector:
            raise ValueError(f"Unknown tab name: {tab_name!r}. Expected one of {list(tab_selectors)}")
        self.page.locator(selector).click()
        _log.debug("Switched to tab: %r", tab_name)

    def get_active_tab_name(self) -> str:
        """Return the text of the currently active (aria-selected / active) tab button."""
        for tab_name, selector in [
            ("Property Type", self._TAB_PROP_TYPE),
            ("Price",         self._TAB_PRICE),
            ("Bedroom",       self._TAB_BEDROOM),
        ]:
            btn = self.page.locator(selector)
            if btn.get_attribute("aria-selected") == "true" or "active" in (btn.get_attribute("class") or ""):
                _log.debug("Active tab: %r", tab_name)
                return tab_name
        return ""

    def is_modal_open(self) -> bool:
        return is_visible(self.modal, timeout=2_000)

    def close_modal_via_escape(self) -> None:
        """Close the modal by pressing Escape without applying changes."""
        _log.info("Closing Quick Filters modal via Escape")
        self.page.keyboard.press("Escape")
        self.modal.wait_for(state="hidden", timeout=5_000)
        _log.debug("Quick Filters modal closed")

    # ── Property Type tab

    def select_property_type(self, prop_type: str) -> None:
        """Click the visible label chip; the hidden radio updates state."""
        _log.info("Selecting property type: %r", prop_type)
        self.property_type_group.locator("label", has_text=prop_type).click()

    def get_selected_property_type(self) -> str:
        for radio in self.property_type_group.get_by_role("radio").all():
            if radio.is_checked():
                return radio.get_attribute("value") or radio.inner_text()
        return ""

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

    def select_bedroom(self, *bedrooms: str) -> None:
        """Click the visible label chips; hidden checkboxes update state."""
        for bedroom in bedrooms:
            _log.info("Selecting bedroom checkbox: %r", bedroom)
            self.bedroom_group.locator("label", has_text=bedroom).click()

    def get_selected_bedrooms(self) -> list[str]:
        selected = []
        for cb in self.bedroom_group.get_by_role("checkbox").all():
            if cb.is_checked():
                selected.append(cb.get_attribute("value") or cb.inner_text())
        _log.debug("Selected bedrooms: %s", selected)
        return selected

    def apply_filters(self) -> None:
        _log.info("Applying quick filters")
        wait_for_search_response(self.page, action=self.apply_button.click)
        try:
            self.modal.wait_for(state="hidden", timeout=5_000)
            _log.debug("Modal closed after Apply")
        except PWTimeoutError:
            _log.warning("Modal did not auto-close after Apply")
        _log.info("Quick filters applied")

    def clear_filters(self) -> None:
        _log.info("Clearing quick filter selections")
        self.clear_button.click()

    def wait_for_results(self, timeout: int = 15_000) -> None:
        self.listing_cards.first.wait_for(state="visible", timeout=timeout)
        count = self.listing_cards.count()
        _log.info("Results loaded: %d listing card(s) visible", count)

    def get_listing_count(self) -> int:
        count = self.listing_cards.count()
        _log.debug("Listing count: %d", count)
        return count

    def is_apply_button_enabled(self) -> bool:
        return self.apply_button.is_enabled()
