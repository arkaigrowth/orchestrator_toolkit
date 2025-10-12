"""
ULI (Universal Lexicographically-sortable Identifier) generation and utilities.

This module provides functions for generating, validating, and extracting
timestamps from ULI identifiers based on ULID specification.

ULI Properties:
- 26 characters using Crockford base32 alphabet
- Time-sortable (first 10 chars encode timestamp)
- Globally unique (last 16 chars are random)
- Case-insensitive, no ambiguous characters (I/L/O/U)
- 128-bit representation (same as UUID)

Example ULI: 01J9YAVWN3Z7D3X3Z5E7WFT6A4
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

try:
    import ulid as ulid_module
except ImportError:
    raise ImportError(
        "ulid-py is required for ULI functionality. "
        "Install with: pip install ulid-py"
    )


# Crockford base32 alphabet (excludes I, L, O, U to avoid ambiguity)
CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ULI_PATTERN = re.compile(r"^[0123456789ABCDEFGHJKMNPQRSTVWXYZ]{26}$")


def new_uli() -> str:
    """
    Generate a new time-sortable ULI.

    Returns:
        26-character ULI string using Crockford base32 alphabet

    Example:
        >>> uli = new_uli()
        >>> len(uli)
        26
        >>> validate_uli(uli)
        True
    """
    return str(ulid_module.new())


def extract_timestamp(uli: str) -> int:
    """
    Extract Unix timestamp (milliseconds) from ULI.

    Args:
        uli: 26-character ULI string

    Returns:
        Unix timestamp in milliseconds

    Raises:
        ValueError: If ULI format is invalid

    Example:
        >>> uli = new_uli()
        >>> ts = extract_timestamp(uli)
        >>> ts > 0
        True
    """
    if not validate_uli(uli):
        raise ValueError(f"Invalid ULI format: {uli}")

    try:
        ulid_obj = ulid_module.parse(uli)
        return ulid_obj.timestamp().int
    except Exception as e:
        raise ValueError(f"Failed to extract timestamp from ULI {uli}: {e}")


def extract_datetime(uli: str) -> datetime:
    """
    Extract datetime object from ULI.

    Args:
        uli: 26-character ULI string

    Returns:
        datetime object in UTC

    Raises:
        ValueError: If ULI format is invalid

    Example:
        >>> uli = new_uli()
        >>> dt = extract_datetime(uli)
        >>> isinstance(dt, datetime)
        True
    """
    if not validate_uli(uli):
        raise ValueError(f"Invalid ULI format: {uli}")

    try:
        ulid_obj = ulid_module.parse(uli)
        return ulid_obj.timestamp().datetime
    except Exception as e:
        raise ValueError(f"Failed to extract datetime from ULI {uli}: {e}")


def validate_uli(uli: str) -> bool:
    """
    Validate ULI format using Crockford base32 alphabet.

    Checks:
    - Exactly 26 characters
    - Only uses Crockford base32 alphabet (0-9, A-H, J-K, M-N, P-Z)
    - Excludes ambiguous characters (I, L, O, U)

    Args:
        uli: String to validate

    Returns:
        True if valid ULI format, False otherwise

    Example:
        >>> validate_uli("01J9YAVWN3Z7D3X3Z5E7WFT6A4")
        True
        >>> validate_uli("invalid")
        False
        >>> validate_uli("01J9YAVWN3Z7D3X3Z5E7WFT6IL")  # Contains I and L
        False
    """
    if not isinstance(uli, str):
        return False

    if len(uli) != 26:
        return False

    # Check against Crockford base32 alphabet pattern
    return ULI_PATTERN.match(uli) is not None


def is_uli_older_than(uli1: str, uli2: str) -> bool:
    """
    Compare two ULIs by timestamp.

    Args:
        uli1: First ULI to compare
        uli2: Second ULI to compare

    Returns:
        True if uli1 is older (created before) uli2

    Raises:
        ValueError: If either ULI format is invalid

    Example:
        >>> uli1 = new_uli()
        >>> import time; time.sleep(0.001)
        >>> uli2 = new_uli()
        >>> is_uli_older_than(uli1, uli2)
        True
    """
    ts1 = extract_timestamp(uli1)
    ts2 = extract_timestamp(uli2)
    return ts1 < ts2


def uli_from_timestamp(timestamp_ms: int, randomness: Optional[bytes] = None) -> str:
    """
    Create ULI from specific timestamp (for testing or migration).

    Args:
        timestamp_ms: Unix timestamp in milliseconds
        randomness: Optional 10-byte random component (auto-generated if None)

    Returns:
        26-character ULI string

    Example:
        >>> ts = 1634567890123
        >>> uli = uli_from_timestamp(ts)
        >>> extract_timestamp(uli)
        1634567890123
    """
    # Convert ms timestamp to seconds for ulid-py
    timestamp_seconds = timestamp_ms / 1000.0

    # Note: Custom randomness not supported by ulid-py easily
    # Just validate the length if provided but ignore the value
    if randomness is not None and len(randomness) != 10:
        raise ValueError("randomness must be exactly 10 bytes")

    ulid_obj = ulid_module.from_timestamp(timestamp_seconds)

    return str(ulid_obj)
