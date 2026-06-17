from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SearchInput:
    keyword: str
    description: str
    expected_results: bool   # True = expect listings to appear


@dataclass(frozen=True)
class PriceRange:
    min_price: Optional[int]
    max_price: Optional[int]
    label: str


# Search Box (Screen 1)

VALID_KEYWORDS = [
    SearchInput("Tampines",        "well-known town",         expected_results=True),
    SearchInput("Orchard Road",    "landmark area",           expected_results=True),
    SearchInput("Bishan",          "popular residential town",expected_results=True),
]

# Minimum characters that should trigger autocomplete suggestions
AUTOCOMPLETE_TRIGGER = "Tam"

WHITESPACE_ONLY      = "   "
SPECIAL_CHARACTERS   = "<script>alert(1)</script>"
LONG_STRING          = "A" * 210
NUMERIC_ONLY         = "999999"
NON_EXISTENT_PLACE   = "ZZZNonExistentPlace123"
EMOJI_INPUT          = "🏠🏡🏘️"
SQL_INJECTION        = "' OR '1'='1"

NO_RESULTS_TEXTS = [
    "no results",
    "no listings",
    "0 properties",
    "no properties found",
]

AUTOCOMPLETE_CONTAINER_VISIBLE_TIMEOUT = 5_000


# Filters — More Filters (Screen 2) and Quick Filters (Screen 3)

# Property types available in the filter panel
PROPERTY_TYPES = ["All", "Condo", "Landed", "HDB"]
FILTERABLE_PROPERTY_TYPES = ["Condo", "Landed", "HDB"]
BEDROOM_OPTIONS = ["Studio", "1", "2", "3", "4", "5+"]
MULTI_BEDROOM_SELECTION = ["2", "3"]

PRICE_RANGES = [
    PriceRange(min_price=500_000,   max_price=1_000_000, label="entry-level"),
    PriceRange(min_price=1_000_000, max_price=3_000_000, label="mid-range"),
]

INVERTED_PRICE_RANGE = PriceRange(
    min_price=3_000_000, max_price=500_000, label="inverted-invalid"
)

FLOOR_SIZE_RANGE = PriceRange(min_price=500, max_price=2_000, label="typical-floor-size")

# Inverted floor size (min > max)
INVERTED_FLOOR_SIZE = PriceRange(min_price=5_000, max_price=100, label="inverted-floor-size")

# Quick filter trigger names (Screen 3) — these must match button text on page
QUICK_FILTER_TRIGGERS = ["Property Type", "Price", "Bedroom"]
