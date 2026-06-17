# E2E tests for the Quick Filters tabbed modal (Screen 3)

import pytest
from playwright.sync_api import expect

from pages.quick_filters_page import QuickFiltersPage
from utils.test_data import (
    FILTERABLE_PROPERTY_TYPES,
    PRICE_RANGES,
    INVERTED_PRICE_RANGE,
    MULTI_BEDROOM_SELECTION,
    QUICK_FILTER_TRIGGERS,
)
from utils.helpers import assert_no_js_errors, assert_no_crash


class TestQuickFiltersHappyPath:

    def test_property_type_button_visible(
        self, quick_filters_page: QuickFiltersPage
    ):
        """Property Type trigger button is visible and clickable on page load."""
        btn = quick_filters_page.page.locator(
            quick_filters_page._PROP_TYPE_TRIGGER
        ).first
        expect(btn).to_be_visible()
        expect(btn).to_be_enabled()

    def test_price_button_visible(self, quick_filters_page: QuickFiltersPage):
        """Price trigger button is visible and clickable on page load."""
        btn = quick_filters_page.page.locator(
            quick_filters_page._PRICE_TRIGGER
        ).first
        expect(btn).to_be_visible()
        expect(btn).to_be_enabled()

    def test_bedroom_button_visible(self, quick_filters_page: QuickFiltersPage):
        """Bedroom trigger button is visible and clickable on page load."""
        btn = quick_filters_page.page.locator(
            quick_filters_page._BEDROOM_TRIGGER
        ).first
        expect(btn).to_be_visible()
        expect(btn).to_be_enabled()

    # ── Trigger → correct tab opens

    def test_property_type_trigger_opens_property_type_tab(
        self, quick_filters_page: QuickFiltersPage
    ):
        """Clicking Property Type trigger opens the modal with the Property Type group visible."""
        quick_filters_page.open_property_type_filter()
        expect(quick_filters_page.property_type_group).to_be_visible()
        # All radio options should be present
        for option in ["All", "Condo", "Landed", "HDB"]:
            expect(
                quick_filters_page.property_type_group.get_by_role("radio", name=option)
            ).to_be_visible()

    def test_price_trigger_opens_price_tab(
        self, quick_filters_page: QuickFiltersPage
    ):
        """Clicking Price trigger opens the modal with min/max price inputs visible."""
        quick_filters_page.open_price_filter()
        expect(quick_filters_page.price_min_input).to_be_visible()
        expect(quick_filters_page.price_max_input).to_be_visible()

    def test_bedroom_trigger_opens_bedroom_tab(
        self, quick_filters_page: QuickFiltersPage
    ):
        """Clicking Bedroom trigger opens the modal with bedroom checkboxes visible."""
        quick_filters_page.open_bedroom_filter()
        group = quick_filters_page.bedroom_group
        expect(group).to_be_visible()
        for bedroom in ["Studio", "1", "2", "3", "4", "5+"]:
            expect(group.get_by_role("checkbox", name=bedroom)).to_be_visible()

    # ── Tab switching

    def test_can_switch_between_tabs(self, quick_filters_page: QuickFiltersPage):
        """Switching tabs inside the modal updates the visible tabpanel content."""
        quick_filters_page.open_property_type_filter()
        # Verify Property Type content is visible
        expect(quick_filters_page.property_type_group).to_be_visible()

        # Switch to Price tab
        quick_filters_page.switch_to_tab("Price")
        expect(quick_filters_page.price_min_input).to_be_visible()

        # Switch to Bedroom tab
        quick_filters_page.switch_to_tab("Bedroom")
        expect(quick_filters_page.bedroom_group).to_be_visible()

        assert_no_crash(quick_filters_page.page)

    # ── Property Type filtering

    @pytest.mark.parametrize(
        "prop_type", FILTERABLE_PROPERTY_TYPES, ids=lambda p: p
    )
    def test_filter_by_property_type_returns_results(
        self, quick_filters_page: QuickFiltersPage, prop_type: str, js_errors
    ):
        """Selecting a property type chip and applying returns non-empty listings."""
        quick_filters_page.open_property_type_filter()
        quick_filters_page.select_property_type(prop_type)
        quick_filters_page.apply_filters()
        quick_filters_page.wait_for_results()

        assert quick_filters_page.get_listing_count() > 0, (
            f"Expected listings after quick-filtering by '{prop_type}', "
            f"but found none."
        )
        assert_no_js_errors(quick_filters_page.page, js_errors)

    # ── Price filtering

    @pytest.mark.parametrize(
        "price_range", PRICE_RANGES, ids=lambda p: p.label
    )
    def test_filter_by_price_range_does_not_crash(
        self, quick_filters_page: QuickFiltersPage, price_range, js_errors
    ):
        """Applying a valid price range does not crash the page."""
        quick_filters_page.open_price_filter()
        quick_filters_page.set_price_range(price_range.min_price, price_range.max_price)
        quick_filters_page.apply_filters()
        quick_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(quick_filters_page.page)
        assert_no_js_errors(quick_filters_page.page, js_errors)

    # ── Bedroom filtering

    def test_filter_by_single_bedroom_returns_results(
        self, quick_filters_page: QuickFiltersPage, js_errors
    ):
        """Selecting a single bedroom count and applying returns non-empty listings."""
        quick_filters_page.open_bedroom_filter()
        quick_filters_page.select_bedroom("2")
        quick_filters_page.apply_filters()
        quick_filters_page.wait_for_results()

        assert quick_filters_page.get_listing_count() > 0, (
            "Expected listings for '2 bedroom' quick filter, but found none."
        )
        assert_no_js_errors(quick_filters_page.page, js_errors)

    def test_filter_by_multiple_bedrooms_returns_results(
        self, quick_filters_page: QuickFiltersPage, js_errors
    ):
        """Selecting multiple bedroom counts returns non-empty listings."""
        quick_filters_page.open_bedroom_filter()
        quick_filters_page.select_bedroom(*MULTI_BEDROOM_SELECTION)
        quick_filters_page.apply_filters()
        quick_filters_page.wait_for_results()

        assert quick_filters_page.get_listing_count() > 0, (
            f"Expected listings for bedroom filter {MULTI_BEDROOM_SELECTION}, "
            "but found none."
        )
        assert_no_js_errors(quick_filters_page.page, js_errors)

    # ── Clear / reset

    def test_clear_button_resets_property_type_to_all(
        self, quick_filters_page: QuickFiltersPage
    ):
        """Clicking Clear after selecting a property type re-selects 'All'."""
        quick_filters_page.open_property_type_filter()
        quick_filters_page.select_property_type("Condo")

        # Confirm Condo is selected
        assert quick_filters_page.property_type_group.get_by_role(
            "radio", name="Condo"
        ).is_checked(), "Condo should be selected before clearing."

        quick_filters_page.clear_filters()

        # 'All' should be re-selected
        assert quick_filters_page.property_type_group.get_by_role(
            "radio", name="All"
        ).is_checked(), (
            "After clicking Clear, 'All' property type was not re-selected."
        )

    def test_clear_button_resets_bedroom_selection(
        self, quick_filters_page: QuickFiltersPage
    ):
        """Clicking Clear after checking bedrooms unchecks all of them."""
        quick_filters_page.open_bedroom_filter()
        quick_filters_page.select_bedroom(*MULTI_BEDROOM_SELECTION)
        quick_filters_page.clear_filters()

        # All bedroom checkboxes should now be unchecked
        group = quick_filters_page.bedroom_group
        for bedroom in MULTI_BEDROOM_SELECTION:
            assert not group.get_by_role("checkbox", name=str(bedroom)).is_checked(), (
                f"Bedroom '{bedroom}' was still checked after clicking Clear."
            )

    # ── Apply / Close

    def test_apply_with_no_changes_does_not_crash(
        self, quick_filters_page: QuickFiltersPage, js_errors
    ):
        """Applying without changing any filter does not crash the page."""
        quick_filters_page.open_property_type_filter()
        quick_filters_page.apply_filters()
        quick_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(quick_filters_page.page)
        assert_no_js_errors(quick_filters_page.page, js_errors)


class TestQuickFiltersNegativePaths:

    def test_inverted_price_range_is_handled_gracefully(
        self, quick_filters_page: QuickFiltersPage, js_errors
    ):
        """An inverted price range (min > max) does not crash the page."""
        quick_filters_page.open_price_filter()
        quick_filters_page.set_price_range(
            INVERTED_PRICE_RANGE.min_price,
            INVERTED_PRICE_RANGE.max_price,
        )
        # The Apply button may be disabled, or may apply (and swap values)
        if quick_filters_page.is_apply_button_enabled():
            quick_filters_page.apply_filters()
            quick_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(quick_filters_page.page)
        assert_no_js_errors(quick_filters_page.page, js_errors)

    def test_escape_closes_modal_without_applying(
        self, quick_filters_page: QuickFiltersPage
    ):
        """Pressing Escape closes the modal without applying the selected filter."""
        quick_filters_page.open_property_type_filter()
        quick_filters_page.select_property_type("Landed")
        quick_filters_page.close_modal_via_escape()

        assert not quick_filters_page.is_modal_open(), (
            "Quick Filters modal did not close after pressing Escape."
        )
        assert_no_crash(quick_filters_page.page)

    def test_rapid_open_close_cycles_are_stable(
        self, quick_filters_page: QuickFiltersPage, js_errors
    ):
        """Rapidly opening and closing the modal three times stays stable."""
        triggers = [
            quick_filters_page.open_property_type_filter,
            quick_filters_page.open_price_filter,
            quick_filters_page.open_bedroom_filter,
        ]
        for i, open_fn in enumerate(triggers):
            open_fn()
            assert quick_filters_page.is_modal_open(), (
                f"Modal was not open on cycle {i + 1}."
            )
            quick_filters_page.close_modal_via_escape()
            assert not quick_filters_page.is_modal_open(), (
                f"Modal was still open after Escape on cycle {i + 1}."
            )
        assert_no_js_errors(quick_filters_page.page, js_errors)