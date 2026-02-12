"""Reusable functions for normalizing CSV data during ETL processes."""

from typing import Optional


def normalize_bool(value: Optional[str]) -> bool:
    """Convert CSV values like '1', 'true', 'yes' to boolean."""
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "oui"}


def normalize_int(value: Optional[str]) -> Optional[int]:
    """Convert CSV string to integer, returning None for empty/invalid values."""
    if value in ("", None):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def normalize_key(value: str) -> str:
    """Normalize string to lowercase for consistent lookups."""
    return value.strip().lower()


def normalize_float(value: Optional[str]) -> Optional[float]:
    """Convert CSV string to float, returning None for empty/invalid values."""
    if value in ("", None):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def normalize_string(value: Optional[str], default: str = "") -> str:
    """Strip whitespace and return default if empty."""
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default
