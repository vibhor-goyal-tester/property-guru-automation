# utils/logger.py
# Central logger factory.
# All modules call get_logger(__name__) to obtain a named logger.
# Configuration (level, format, handlers) is driven by pytest.ini / logging.ini
# so pytest can capture records and embed them in the HTML report automatically.

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a standard Logger scoped to `name` (typically __name__)."""
    return logging.getLogger(name)
