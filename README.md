# PropertyGuru Automation — Screen 1: Search Box

End-to-end test suite for the Search Box experience on [propertyguru.com.sg/property-for-sale](https://www.propertyguru.com.sg/property-for-sale).

Built with **Python + Playwright + pytest**.

---

## Project Structure

```
propertyguru-automation/
├── pages/
│   ├── base_page.py          # Shared navigation, cookie dismissal
│   └── search_box_page.py    # Screen 1 — all search box interactions
├── tests/
│   └── test_search_box.py    # Happy path + negative path tests
├── utils/
│   ├── test_data.py          # All test inputs in one place
│   └── helpers.py            # Wait helpers, JS error collectors
├── conftest.py               # Shared pytest fixtures (browser, page, page objects)
├── playwright.config.py      # Timeouts, viewport, headless toggle
├── pytest.ini                # pytest settings and HTML report config
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. (Optional) Install rerun plugin for flaky test retries

```bash
pip install pytest-rerunfailures
```

---

## Running Tests

### Run all Search Box tests

```bash
pytest tests/test_search_box.py
```

### Run with live browser (watch mode)

```bash
HEADLESS=false pytest tests/test_search_box.py
```

### Run a specific test

```bash
pytest tests/test_search_box.py::TestSearchBoxHappyPath::test_valid_keyword_returns_listings
```

### Run only happy path tests

```bash
pytest tests/test_search_box.py -k "HappyPath"
```

### Run only negative path tests

```bash
pytest tests/test_search_box.py -k "NegativePaths"
```

### Slow down actions for debugging

```bash
HEADLESS=false SLOW_MO=500 pytest tests/test_search_box.py
```

### View HTML report after run

```bash
open reports/report.html   # macOS
xdg-open reports/report.html  # Linux
```

---

## Test Coverage — Screen 1 (Search Box)

| # | Test | Type |
|---|------|------|
| 1 | Search box visible on page load | Happy |
| 2 | Valid keyword returns listings (parametrized × 3 locations) | Happy |
| 3 | Autocomplete appears after 3+ characters | Happy |
| 4 | Autocomplete suggestions are relevant to typed prefix | Happy |
| 5 | Clicking autocomplete suggestion shows results | Happy |
| 6 | Enter key submits search and returns results | Happy |
| 7 | Clear button empties input and resets listings | Happy |
| 8 | Result count header reflects search | Happy |
| 9 | URL reflects search term (shareable links) | Happy |
| 10 | Whitespace-only input doesn't crash | Negative |
| 11 | Special characters / XSS probe — no alert dialogs | Negative |
| 12 | Very long string (210 chars) — truncated or handled | Negative |
| 13 | Non-existent place — empty state shown | Negative |
| 14 | Numeric-only input — no crash | Negative |
| 15 | Emoji input — no crash | Negative |
| 16 | SQL injection probe — no DB error leakage | Negative |
| 17 | Rapid successive searches — no ghost results | Negative |
| 18 | Empty submit — stays on listing page | Negative |

---

## Selector Maintenance

All selectors live in `pages/search_box_page.py` under the `_SELECTORS` block.  
If PropertyGuru updates their UI, update **only** the selector constants — no test changes needed.

**Selector priority order used:**
1. `data-testid` — most stable
2. `aria-label` — accessible, survives CSS refactors
3. `placeholder` — stable UX copy
4. CSS class — last resort

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADLESS` | `true` | Set to `false` to watch tests |
| `SLOW_MO` | `0` | Milliseconds between actions (debug) |

---

## Adding More Screens

- Add `pages/quick_filter_page.py` for Screen 3
- Add `pages/more_filters_page.py` for Screen 2
- Add corresponding test files in `tests/`
- Fixtures in `conftest.py` will automatically pick them up
