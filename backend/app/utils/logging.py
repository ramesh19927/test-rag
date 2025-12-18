"""Structured logging helpers."""
import logging
from typing import Optional


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure a root logger with JSON-friendly format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    return logging.getLogger("app")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-level logger after base configuration."""
    return logging.getLogger(name or "app")
