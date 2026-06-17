# PropertyGuru Automation — Search Box, More Filters & Quick Filters

End-to-end test suite for three key screens on [propertyguru.com.sg/property-for-sale](https://www.propertyguru.com.sg/property-for-sale):

- **Screen 1** — Search Box
- **Screen 2** — More Filters modal
- **Screen 3** — Quick Filters tabbed modal

Built with **Python + Playwright + pytest**.

---

## Project Structure

```
propertyguru-automation/
├── pages/
│   ├── base_page.py            # Shared navigation, cookie dismissal
│   ├── search_box_page.py      # Screen 1 — search box interactions
│   ├── more_filters_page.py    # Screen 2 — More Filters modal interactions
│   └── quick_filters_page.py   # Screen 3 — Quick Filters tabbed modal interactions
├── tests/
│   ├── test_search_box.py      # Screen 1 — happy path + negative path tests
│   ├── test_more_filters.py    # Screen 2 — happy path + negative path tests
│   └── test_quick_filters.py   # Screen 3 — happy path + negative path tests
├── utils/
│   ├── test_data.py            # All test inputs in one place
│   ├── helpers.py              # Wait helpers, JS error collectors
│   └── logger.py               # Named logger factory (used by all modules)
├── conftest.py                 # Shared pytest fixtures (browser, page, page objects)
├── playwright_config.py        # Timeouts, viewport, user-agent, headless toggle
├── pytest.ini                  # pytest settings, HTML report, and log config
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

All required packages — including `pytest-rerunfailures` for flaky-test retries — are listed in `requirements.txt`.

---

## Running Tests

### Run all tests

```bash
pytest
```

### Run a specific screen

```bash
pytest tests/test_search_box.py
pytest tests/test_more_filters.py
pytest tests/test_quick_filters.py
```

### Run with live browser (watch mode)

```bash
$env:HEADLESS="false"; pytest          # PowerShell
HEADLESS=false pytest                  # bash / macOS / Linux
```

> **Cloudflare human-verification check**  
> PropertyGuru occasionally serves a Cloudflare challenge ("Verify you are human") before loading the page.
> Automated browsers cannot pass this automatically.  
> If a test errors out at navigation/page load, run in headed mode (`HEADLESS=false`) and manually click the verification checkbox when the Cloudflare screen appears — the browser will stay open and the remaining tests will continue once the challenge is cleared.

### Run a specific test

```bash
pytest tests/test_search_box.py::TestSearchBoxHappyPath::test_valid_keyword_returns_listings
```

### Run only happy path or negative path tests

```bash
pytest -k "HappyPath"
pytest -k "NegativePaths"
```

### Slow down actions for debugging

```bash
$env:HEADLESS="false"; $env:SLOW_MO="500"; pytest    # PowerShell
HEADLESS=false SLOW_MO=500 pytest                    # bash / macOS / Linux
```

### View reports after a run

```bash
# HTML report
start reports/report.html        # Windows
open reports/report.html         # macOS
xdg-open reports/report.html     # Linux

# Full debug log
cat reports/test_run.log
```

---

## Test Coverage

### Screen 1 — Search Box (`test_search_box.py`)

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
| 17 | Rapid successive searches — UI stays stable | Negative |
| 18 | Empty submit — no error navigation | Negative |

### Screen 2 — More Filters (`test_more_filters.py`)

| # | Test | Type |
|---|------|------|
| 1 | Filters button visible and enabled on page load | Happy |
| 2 | Clicking Filters button opens modal | Happy |
| 3 | Modal has Property Type section (All / Condo / Landed / HDB) | Happy |
| 4 | Modal has Price section with min and max inputs | Happy |
| 5 | Modal has Bedroom section (Studio through 5+) | Happy |
| 6 | Modal has enabled Apply and Clear buttons | Happy |
| 7 | Filtering by property type returns results (parametrized × 3 types) | Happy |
| 8 | Filtering by price range does not crash (parametrized × 2 ranges) | Happy |
| 9 | Filtering by single bedroom count returns results | Happy |
| 10 | Filtering by multiple bedroom counts returns results | Happy |
| 11 | Combined property type + bedroom filter returns results | Happy |
| 12 | Clear resets selections and re-selects All property type | Happy |
| 13 | Close button dismisses modal without applying | Happy |
| 14 | Escape key closes modal | Happy |
| 15 | Inverted price range (min > max) — no crash | Negative |
| 16 | Inverted floor size range (min > max) — no crash | Negative |
| 17 | Extremely high price value — no crash | Negative |
| 18 | Opening and closing modal repeatedly stays stable | Negative |
| 19 | Apply with no changes — no crash | Negative |

### Screen 3 — Quick Filters (`test_quick_filters.py`)

| # | Test | Type |
|---|------|------|
| 1 | Property Type trigger button visible and enabled | Happy |
| 2 | Price trigger button visible and enabled | Happy |
| 3 | Bedroom trigger button visible and enabled | Happy |
| 4 | Property Type trigger opens modal with Property Type tab | Happy |
| 5 | Price trigger opens modal with Price tab | Happy |
| 6 | Bedroom trigger opens modal with Bedroom tab | Happy |
| 7 | Can switch between tabs inside the modal | Happy |
| 8 | Filter by property type returns results (parametrized × 3 types) | Happy |
| 9 | Filter by price range does not crash (parametrized × 2 ranges) | Happy |
| 10 | Filter by single bedroom returns results | Happy |
| 11 | Filter by multiple bedrooms returns results | Happy |
| 12 | Clear resets Property Type to All | Happy |
| 13 | Clear resets bedroom selection | Happy |
| 14 | Apply with no changes — no crash | Happy |
| 15 | Inverted price range (min > max) — no crash | Negative |
| 16 | Escape closes modal without applying | Negative |
| 17 | Rapid open/close cycles stay stable | Negative |

---

## Selector Maintenance

All selectors live in the corresponding page object under the `_SELECTORS` / `_*` block.  
If PropertyGuru updates their UI, update **only** the selector constants — no test changes needed.

**Selector priority order used:**
1. `data-testid` — most stable
2. `aria-label` — accessible, survives CSS refactors
3. `placeholder` — stable UX copy
4. CSS class — last resort

---

## Logging

Logging is configured in `pytest.ini`:

| Destination | Level | Location |
|-------------|-------|----------|
| Console (live) | `INFO` | terminal during the run |
| HTML report | `DEBUG` | embedded per-test in `reports/report.html` |
| Log file | `DEBUG` | `reports/test_run.log` (overwritten each run) |

All modules obtain a logger via `utils/logger.py`:

```python
from utils.logger import get_logger
_log = get_logger(__name__)
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADLESS` | `true` | Set to `false` to watch tests run |
| `SLOW_MO` | `0` | Milliseconds between actions (useful for debugging) |
