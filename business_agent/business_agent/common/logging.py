from __future__ import annotations

import logging
from typing import TextIO


def configure_logging(
    level: str = "INFO",
    *,
    stream: TextIO | None = None,
) -> logging.Logger:
    """Configure and return the platform logger without duplicating handlers."""
    logger = logging.getLogger("business_agent")
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    if not logger.handlers:
        handler = logging.StreamHandler(stream)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s - %(message)s"
            )
        )
        logger.addHandler(handler)

    logger.propagate = False
    return logger
