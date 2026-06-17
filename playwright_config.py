import os

BASE_URL = "https://www.propertyguru.com.sg/property-for-sale"

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))
DEFAULT_TIMEOUT = 15_000
VIEWPORT = {"width": 1440, "height": 900}

# Mimic a real Chrome UA to avoid bot detection
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

RETRIES = 1
