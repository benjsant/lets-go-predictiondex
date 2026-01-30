"""
Data Normalization Utilities for ETL
=====================================

Reusable functions for normalizing CSV data during ETL processes.
Eliminates code duplication across ETL scripts.
"""

from typing import Optional


def normalize_bool(value: Optional[str]) -> bool:
    """
    Normalize boolean-like CSV values.

    Accepted truthy values: 1, true, yes, oui (case-insensitive).

    Args:
        value: Raw CSV value

    Returns:
        Boolean representation

    Examples:
        >>> normalize_bool("1")
        True
        >>> normalize_bool("yes")
        True
        >>> normalize_bool("0")
        False
    """
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "oui"}


def normalize_int(value: Optional[str]) -> Optional[int]:
    """
    Convert optional integer CSV values.

    Empty strings or None are converted to None.

    Args:
        value: Raw CSV value

    Returns:
        Integer value or None

    Examples:
        >>> normalize_int("42")
        42
        >>> normalize_int("")
        None
        >>> normalize_int(None)
        None
    """
    if value in ("", None):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def normalize_key(value: str) -> str:
    """
    Normalize string keys for consistent lookups.

    Converts to lowercase and strips whitespace.

    Args:
        value: Raw string value

    Returns:
        Normalized lowercase key

    Examples:
        >>> normalize_key("  Fire  ")
        'fire'
        >>> normalize_key("WATER")
        'water'
    """
    return value.strip().lower()


def normalize_float(value: Optional[str]) -> Optional[float]:
    """
    Convert optional float CSV values.

    Empty strings or None are converted to None.

    Args:
        value: Raw CSV value

    Returns:
        Float value or None

    Examples:
        >>> normalize_float("3.14")
        3.14
        >>> normalize_float("")
        None
    """
    if value in ("", None):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def normalize_string(value: Optional[str], default: str = "") -> str:
    """
    Normalize optional string values.

    Strips whitespace and converts None to default value.

    Args:
        value: Raw string value
        default: Default value if input is None or empty

    Returns:
        Normalized string

    Examples:
        >>> normalize_string("  hello  ")
        'hello'
        >>> normalize_string(None, "default")
        'default'
    """
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default
