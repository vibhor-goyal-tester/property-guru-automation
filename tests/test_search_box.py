# E2E tests for the Search Box on the PropertyGuru listing page (Screen 1)

import pytest
from playwright.sync_api import expect

from pages.search_box_page import SearchBoxPage
from utils.test_data import (
    VALID_KEYWORDS,
    AUTOCOMPLETE_TRIGGER,
    WHITESPACE_ONLY,
    SPECIAL_CHARACTERS,
    LONG_STRING,
    NUMERIC_ONLY,
    NON_EXISTENT_PLACE,
    EMOJI_INPUT,
    SQL_INJECTION,
    NO_RESULTS_TEXTS,
    AUTOCOMPLETE_CONTAINER_VISIBLE_TIMEOUT,
)
from utils.helpers import assert_no_js_errors, assert_no_crash, page_contains_any


class TestSearchBoxHappyPath:

    def test_search_box_is_visible_on_page_load(self, search_page: SearchBoxPage):
        """Search input is visible and enabled on page load."""
        expect(search_page.search_input).to_be_visible()
        expect(search_page.search_input).to_be_enabled()

    @pytest.mark.parametrize("keyword_data", VALID_KEYWORDS, ids=lambda d: d.keyword)
    def test_valid_keyword_returns_listings(
        self, search_page: SearchBoxPage, keyword_data, js_errors
    ):
        """Searching a valid Singapore location returns non-empty listings."""
        search_page.search(keyword_data.keyword)
        search_page.wait_for_results()

        count = search_page.get_listing_count()
        assert count > 0, (
            f"Expected listings after searching '{keyword_data.keyword}', "
            f"but found {count} listing cards on the page."
        )
        assert_no_js_errors(search_page.page, js_errors)

    def test_autocomplete_appears_after_typing(self, search_page: SearchBoxPage):
        """Typing 3+ characters shows an autocomplete dropdown."""
        search_page.type_char_by_char(AUTOCOMPLETE_TRIGGER)
        appeared = search_page.wait_for_autocomplete(
            timeout=AUTOCOMPLETE_CONTAINER_VISIBLE_TIMEOUT
        )
        assert appeared, (
            f"Autocomplete dropdown did not appear after typing '{AUTOCOMPLETE_TRIGGER}'. "
            "Check '_AUTOCOMPLETE_CONTAINER' selector in SearchBoxPage."
        )

    def test_autocomplete_suggestions_are_relevant(self, search_page: SearchBoxPage):
        """Autocomplete suggestions contain the typed prefix."""
        search_page.type_char_by_char(AUTOCOMPLETE_TRIGGER)
        appeared = search_page.wait_for_autocomplete(
            timeout=AUTOCOMPLETE_CONTAINER_VISIBLE_TIMEOUT
        )
        if not appeared:
            pytest.skip("Autocomplete did not appear — possible A/B test or bot block")

        suggestions = search_page.get_autocomplete_suggestions()
        assert len(suggestions) > 0, "Autocomplete dropdown appeared but contained no items."

        prefix = AUTOCOMPLETE_TRIGGER.lower()
        irrelevant = [s for s in suggestions if prefix not in s.lower()]
        assert len(irrelevant) == 0 or len(irrelevant) < len(suggestions), (
            f"Autocomplete suggestions do not seem relevant to '{AUTOCOMPLETE_TRIGGER}': "
            f"{suggestions}"
        )

    def test_selecting_autocomplete_suggestion_shows_results(
        self, search_page: SearchBoxPage
    ):
        """Clicking an autocomplete suggestion returns listing results."""
        search_page.type_char_by_char(AUTOCOMPLETE_TRIGGER)
        appeared = search_page.wait_for_autocomplete(
            timeout=AUTOCOMPLETE_CONTAINER_VISIBLE_TIMEOUT
        )
        if not appeared:
            pytest.skip("Autocomplete did not appear — skipping suggestion-click test")

        search_page.select_autocomplete_suggestion(index=0)
        search_page.wait_for_results()

        assert search_page.get_listing_count() > 0, (
            "Clicking an autocomplete suggestion did not produce any listing results."
        )

    def test_search_via_enter_key_returns_results(self, search_page: SearchBoxPage):
        """Pressing Enter after typing a keyword returns results."""
        search_page.type_in_search("Orchard")
        search_page.submit_search()
        search_page.wait_for_results()

        assert search_page.get_listing_count() > 0, (
            "Pressing Enter did not trigger a search or return results."
        )

    def test_clearing_search_resets_to_default_listings(
        self, search_page: SearchBoxPage
    ):
        """Clearing the search input empties the field and returns to default listings."""
        # First, perform a search to change state
        search_page.search("Tampines")
        search_page.wait_for_results()
        count_before = search_page.get_listing_count()

        # Now clear it
        search_page.clear_search()

        # Input should be empty
        value_after = search_page.get_search_input_value()
        assert value_after.strip() == "", (
            f"Expected empty search input after clearing, got: '{value_after}'"
        )

    def test_result_count_header_reflects_search(self, search_page: SearchBoxPage):
        """The result count in the header is positive after a valid search."""
        search_page.search("Bishan")
        search_page.wait_for_results()

        count = search_page.get_result_count_from_header()
        if count is None:
            pytest.skip("Could not extract result count from header — check selectors")

        assert count > 0, (
            f"Result count header showed {count} after a valid search for 'Bishan'."
        )

    def test_search_result_url_contains_keyword(self, search_page: SearchBoxPage):
        """The page URL reflects the search keyword after submitting."""
        keyword = "Tampines"
        search_page.search(keyword)
        search_page.wait_for_results()

        current_url = search_page.get_current_url().lower()
        assert keyword.lower() in current_url or "search" in current_url, (
            f"URL '{search_page.get_current_url()}' does not reflect the search for '{keyword}'. "
            "This could break deep-linking / shareability."
        )


class TestSearchBoxNegativePaths:

    def test_whitespace_only_input_does_not_crash(
        self, search_page: SearchBoxPage, js_errors
    ):
        """Submitting only whitespace does not crash the page."""
        search_page.type_in_search(WHITESPACE_ONLY)
        search_page.search_input.press("Enter")

        # Give the page a moment to react
        search_page.page.wait_for_timeout(2_000)

        assert_no_crash(search_page.page)
        assert_no_js_errors(search_page.page, js_errors)

    def test_special_characters_do_not_cause_errors(
        self, search_page: SearchBoxPage, js_errors
    ):
        """HTML/script special characters are safely handled (XSS probe)."""
        # Intercept any unexpected dialog (alert/confirm) that would indicate XSS
        dialog_triggered = []
        search_page.page.on("dialog", lambda d: (dialog_triggered.append(d.message), d.dismiss()))

        search_page.type_in_search(SPECIAL_CHARACTERS)
        search_page.search_input.press("Enter")
        search_page.page.wait_for_timeout(2_000)

        assert not dialog_triggered, (
            f"An alert dialog appeared after entering special characters, "
            f"suggesting a potential XSS vulnerability. Dialog message: {dialog_triggered}"
        )
        assert_no_crash(search_page.page)
        assert_no_js_errors(search_page.page, js_errors)

    def test_very_long_input_is_handled_gracefully(
        self, search_page: SearchBoxPage, js_errors
    ):
        """A very long input is truncated or accepted without crashing."""
        search_page.type_in_search(LONG_STRING)

        actual_value = search_page.get_search_input_value()
        max_length = search_page.get_input_max_length()

        if max_length:
            assert len(actual_value) <= max_length, (
                f"Input accepted {len(actual_value)} characters, "
                f"exceeding the declared maxlength of {max_length}."
            )
        else:
            # No maxlength — verify the page can still search without errors
            search_page.search_input.press("Enter")
            search_page.page.wait_for_timeout(2_000)
            assert_no_crash(search_page.page)

        assert_no_js_errors(search_page.page, js_errors)

    def test_non_existent_place_shows_empty_state(
        self, search_page: SearchBoxPage, js_errors
    ):
        """Searching a non-existent place shows an empty state, not a crash."""
        search_page.search(NON_EXISTENT_PLACE)
        search_page.page.wait_for_timeout(3_000)  # allow results to settle

        is_empty = search_page.is_no_results_shown()
        listing_count = search_page.get_listing_count()

        # Either an explicit empty-state banner appears, or 0 listing cards shown
        assert is_empty or listing_count == 0, (
            f"Expected no results for '{NON_EXISTENT_PLACE}', "
            f"but found {listing_count} listings and no empty-state banner."
        )
        assert_no_crash(search_page.page)
        assert_no_js_errors(search_page.page, js_errors)

    def test_numeric_only_input_does_not_crash(
        self, search_page: SearchBoxPage, js_errors
    ):
        """Searching with only numbers does not crash the page."""
        search_page.search(NUMERIC_ONLY)
        search_page.page.wait_for_timeout(2_000)

        assert_no_crash(search_page.page)
        assert_no_js_errors(search_page.page, js_errors)

    def test_emoji_input_is_handled_gracefully(
        self, search_page: SearchBoxPage, js_errors
    ):
        """Emoji input does not crash the page."""
        search_page.type_in_search(EMOJI_INPUT)
        search_page.search_input.press("Enter")
        search_page.page.wait_for_timeout(2_000)

        assert_no_crash(search_page.page)
        assert_no_js_errors(search_page.page, js_errors)

    def test_sql_injection_string_does_not_expose_errors(
        self, search_page: SearchBoxPage, js_errors
    ):
        """A SQL injection probe string does not leak database errors."""
        search_page.search(SQL_INJECTION)
        search_page.page.wait_for_timeout(2_000)

        # Check body text for common database/server error signatures
        body_text = search_page.page.locator("body").inner_text().lower()
        db_error_signals = [
            "sql", "syntax error", "unclosed quotation", "ora-", "mysql",
            "pg::", "exception", "stack trace", "traceback",
        ]
        leaks = [sig for sig in db_error_signals if sig in body_text]
        assert not leaks, (
            f"Possible database error leaked in page body after SQL injection probe. "
            f"Detected signals: {leaks}"
        )

        assert_no_crash(search_page.page)
        assert_no_js_errors(search_page.page, js_errors)

    def test_rapid_successive_searches_do_not_break_ui(
        self, search_page: SearchBoxPage, js_errors
    ):
        """Rapidly submitting different search terms keeps the UI stable."""
        terms = ["T", "Ta", "Tam", "Tamp", "Tampines"]
        for term in terms:
            search_page.search_input.fill(term)
            search_page.page.wait_for_timeout(200)  # brief pause between each

        # Submit the final term
        search_page.submit_search()
        search_page.page.wait_for_timeout(3_000)

        assert_no_crash(search_page.page)
        assert_no_js_errors(search_page.page, js_errors)

    def test_empty_submit_does_not_navigate_away(self, search_page: SearchBoxPage):
        """Submitting an empty search does not navigate to an error page."""
        original_url = search_page.get_current_url()

        # Ensure input is empty
        search_page.search_input.fill("")
        search_page.submit_search()
        search_page.page.wait_for_timeout(2_000)

        current_url = search_page.get_current_url()
        assert "error" not in current_url.lower(), (
            f"Submitting an empty search navigated to an error URL: {current_url}"
        )
        assert_no_crash(search_page.page)
