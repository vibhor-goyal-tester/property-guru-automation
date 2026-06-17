# E2E tests for the More Filters modal (Screen 2)

import pytest
from playwright.sync_api import expect

from pages.more_filters_page import MoreFiltersPage
from utils.test_data import (
    FILTERABLE_PROPERTY_TYPES,
    PRICE_RANGES,
    INVERTED_PRICE_RANGE,
    BEDROOM_OPTIONS,
    MULTI_BEDROOM_SELECTION,
    FLOOR_SIZE_RANGE,
    INVERTED_FLOOR_SIZE,
)
from utils.helpers import assert_no_js_errors, assert_no_crash


class TestMoreFiltersHappyPath:

    def test_filters_button_is_visible_on_page_load(
        self, more_filters_page: MoreFiltersPage
    ):
        """The Filters button is visible and clickable on page load."""
        expect(more_filters_page.filters_button).to_be_visible()
        expect(more_filters_page.filters_button).to_be_enabled()

    def test_filters_button_opens_modal(self, more_filters_page: MoreFiltersPage):
        """Clicking the Filters button opens the modal."""
        more_filters_page.open_modal()
        assert more_filters_page.is_modal_open(), (
            "More Filters modal did not open after clicking the Filters button."
        )

    def test_modal_has_property_type_section(
        self, more_filters_page: MoreFiltersPage
    ):
        """Modal shows the Property Type section with All/Condo/Landed/HDB options."""
        more_filters_page.open_modal()
        group = more_filters_page.property_type_group
        expect(group).to_be_visible()
        # All four property type radios should exist
        for prop_type in ["All", "Condo", "Landed", "HDB"]:
            radio = group.get_by_role("radio", name=prop_type)
            expect(radio).to_be_visible()

    def test_modal_has_price_section(self, more_filters_page: MoreFiltersPage):
        """Modal shows the Price section with min and max spinbuttons."""
        more_filters_page.open_modal()
        expect(more_filters_page.price_min_input).to_be_visible()
        expect(more_filters_page.price_max_input).to_be_visible()

    def test_modal_has_bedroom_section(self, more_filters_page: MoreFiltersPage):
        """Modal shows the Bedroom section with Studio through 5+ options."""
        more_filters_page.open_modal()
        group = more_filters_page.bedroom_group
        expect(group).to_be_visible()
        for bedroom in ["Studio", "1", "2", "3", "4", "5+"]:
            cb = group.get_by_role("checkbox", name=bedroom)
            expect(cb).to_be_visible()

    def test_modal_has_apply_and_clear_buttons(
        self, more_filters_page: MoreFiltersPage
    ):
        """Modal footer has enabled Apply and Clear buttons."""
        more_filters_page.open_modal()
        expect(more_filters_page.apply_button).to_be_visible()
        expect(more_filters_page.apply_button).to_be_enabled()
        expect(more_filters_page.clear_button).to_be_visible()
        expect(more_filters_page.clear_button).to_be_enabled()

    @pytest.mark.parametrize(
        "prop_type", FILTERABLE_PROPERTY_TYPES, ids=lambda p: p
    )
    def test_filtering_by_property_type_returns_results(
        self, more_filters_page: MoreFiltersPage, prop_type: str, js_errors
    ):
        """Filtering by property type returns non-empty listings."""
        more_filters_page.open_modal()
        more_filters_page.select_property_type(prop_type)
        count_before = more_filters_page.get_listing_count()
        more_filters_page.apply_filters()
        more_filters_page.wait_for_results()
        count_after = more_filters_page.get_listing_count()

        assert count_after > 0, (
            f"Expected listings after filtering by '{prop_type}', "
            f"but got {count_after} results."
        )
        assert_no_js_errors(more_filters_page.page, js_errors)

    @pytest.mark.parametrize(
        "price_range", PRICE_RANGES, ids=lambda p: p.label
    )
    def test_filtering_by_price_range_returns_results(
        self, more_filters_page: MoreFiltersPage, price_range, js_errors
    ):
        """Filtering by a valid price range does not crash."""
        more_filters_page.open_modal()
        more_filters_page.set_price_range(price_range.min_price, price_range.max_price)
        more_filters_page.apply_filters()

        # Wait briefly -- results may be zero for narrow ranges, which is valid
        more_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(more_filters_page.page)
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_filtering_by_single_bedroom_returns_results(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """Filtering by a single bedroom count returns listings."""
        more_filters_page.open_modal()
        more_filters_page.select_bedroom("2")
        more_filters_page.apply_filters()
        more_filters_page.wait_for_results()

        assert more_filters_page.get_listing_count() > 0, (
            "Expected listings after selecting 2-bedroom filter, but found none."
        )
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_filtering_by_multiple_bedrooms_returns_results(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """Filtering by multiple bedroom counts returns listings."""
        more_filters_page.open_modal()
        more_filters_page.select_bedroom(*MULTI_BEDROOM_SELECTION)
        more_filters_page.apply_filters()
        more_filters_page.wait_for_results()

        assert more_filters_page.get_listing_count() > 0, (
            f"Expected listings after selecting bedrooms {MULTI_BEDROOM_SELECTION}, "
            "but found none."
        )
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_combined_property_type_and_bedroom_filter(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """Combined property type + bedroom filter returns listings."""
        more_filters_page.open_modal()
        more_filters_page.select_property_type("Condo")
        more_filters_page.select_bedroom("3")
        more_filters_page.apply_filters()
        more_filters_page.wait_for_results()

        assert more_filters_page.get_listing_count() > 0, (
            "Expected listings for Condo + 3-bedroom filter, but found none."
        )
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_clear_button_resets_selections(
        self, more_filters_page: MoreFiltersPage
    ):
        """Clear resets all filters and re-selects 'All' property type."""
        more_filters_page.open_modal()
        # Set some filters
        more_filters_page.select_property_type("Condo")
        more_filters_page.select_bedroom("2")

        # Clear
        more_filters_page.clear_filters()

        # 'All' radio should be checked again (the default)
        all_radio = more_filters_page.property_type_group.get_by_role(
            "radio", name="All"
        )
        assert all_radio.is_checked(), (
            "After clicking Clear, the 'All' property type radio was not re-selected."
        )

    def test_close_button_dismisses_modal_without_applying(
        self, more_filters_page: MoreFiltersPage
    ):
        """The close button dismisses the modal without applying filters."""
        more_filters_page.open_modal()
        more_filters_page.select_property_type("HDB")
        more_filters_page.close_modal_via_button()

        assert not more_filters_page.is_modal_open(), (
            "More Filters modal did not close after clicking the close button."
        )
        assert_no_crash(more_filters_page.page)

    def test_escape_key_closes_modal(self, more_filters_page: MoreFiltersPage):
        """Pressing Escape closes the modal."""
        more_filters_page.open_modal()
        more_filters_page.close_modal_via_escape()

        assert not more_filters_page.is_modal_open(), (
            "More Filters modal did not close when Escape was pressed."
        )


class TestMoreFiltersNegativePaths:

    def test_inverted_price_range_is_handled_gracefully(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """An inverted price range (min > max) does not crash the page."""
        more_filters_page.open_modal()
        more_filters_page.set_price_range(
            INVERTED_PRICE_RANGE.min_price,
            INVERTED_PRICE_RANGE.max_price,
        )
        # The Apply button may be disabled, or may apply (and swap values)
        if more_filters_page.is_apply_button_enabled():
            more_filters_page.apply_filters()
            more_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(more_filters_page.page)
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_inverted_floor_size_is_handled_gracefully(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """An inverted floor size range (min > max) does not crash the page."""
        more_filters_page.open_modal()
        more_filters_page.set_floor_size_range(
            INVERTED_FLOOR_SIZE.min_price,  # re-using PriceRange.min_price for sqft
            INVERTED_FLOOR_SIZE.max_price,
        )
        if more_filters_page.is_apply_button_enabled():
            more_filters_page.apply_filters()
            more_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(more_filters_page.page)
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_extremely_high_price_does_not_crash(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """A very large max price value does not crash the page."""
        more_filters_page.open_modal()
        more_filters_page.set_price_range(max_price=999_999_999)
        if more_filters_page.is_apply_button_enabled():
            more_filters_page.apply_filters()
            more_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(more_filters_page.page)
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_opening_and_closing_modal_repeatedly_is_stable(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """Opening and closing the modal three times in a row stays stable."""
        for cycle in range(3):
            more_filters_page.open_modal()
            assert more_filters_page.is_modal_open(), (
                f"Modal was not open on cycle {cycle + 1}."
            )
            more_filters_page.close_modal_via_button()
            assert not more_filters_page.is_modal_open(), (
                f"Modal was still open after close on cycle {cycle + 1}."
            )
        assert_no_js_errors(more_filters_page.page, js_errors)

    def test_apply_with_no_changes_does_not_crash(
        self, more_filters_page: MoreFiltersPage, js_errors
    ):
        """Applying without changing any filter does not crash."""
        more_filters_page.open_modal()
        more_filters_page.apply_filters()
        more_filters_page.page.wait_for_timeout(2_000)
        assert_no_crash(more_filters_page.page)
        assert_no_js_errors(more_filters_page.page, js_errors)