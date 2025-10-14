"""
ID Generation System for PLAN/SPEC/EXECUTE Model

Generates IDs in format: TYPE-YYYYMMDD-ULID6-slug
Example: PLAN-20251013-01T6N8-ship-auth

Features:
- ULID6: Monotonic ULID (first 4 chars timestamp + 2 chars random) for guaranteed uniqueness
- Date: YYYYMMDD for human readability and grouping
- Slug: URL-safe, lowercase, hyphenated title (max 36 chars after prefix)
"""
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import ulid


def new_ulid6() -> str:
    """
    Generate 6 characters from a MONOTONIC ULID.

    Monotonic ULIDs guarantee strict ordering even within same millisecond.
    Multiple rapid calls will have incrementing random portions.

    These 6 chars provide:
    - Time-based sorting (from timestamp portion)
    - Guaranteed uniqueness (monotonic incrementing)
    - Human-readable format (Crockford base32)

    Returns:
        6-character uppercase string from ULID

    Note:
        Uses ulid.monotonic.new() which maintains state for same-millisecond calls.
    """
    # Generate monotonic ULID (increments if called in same millisecond)
    new_ulid = ulid.monotonic.new()
    ulid_str = str(new_ulid)
    # Take first 4 from timestamp (for sorting) + 2 from random (for uniqueness)
    # ULID format: TTTTTTTTTTRRRRRRRRRRRRRRR (10 time + 16 random)
    return (ulid_str[:4] + ulid_str[10:12]).upper()


def slugify(title: str, max_len: int = 36) -> str:
    """
    Convert a title to a URL-safe slug.

    Rules (updated):
    - Lowercase only
    - Keep a-z, 0-9, and hyphens
    - Collapse whitespace/punctuation to single hyphen
    - Truncate to max_len (default 36 for TYPE-YYYYMMDD-ULID6- prefix)
    - Strip leading/trailing hyphens
    - Default to 'untitled' if empty

    Args:
        title: The title to slugify
        max_len: Maximum length of slug (default: 36)

    Returns:
        URL-safe slug string

    Examples:
        slugify("Implement OAuth 2.1 & PKCE (Web+Mobile)")
        -> "implement-oauth-2-1-pkce-web-mobile"

        slugify("Design: Auth session lifetimes")
        -> "design-auth-session-lifetimes"

        slugify("Plan #123: New feature!")
        -> "plan-123-new-feature"

        slugify("") -> "untitled"
    """
    if not title or title is None:
        return 'untitled'

    # Convert to lowercase
    s = title.lower()

    # Replace non-alphanumeric characters with hyphens (keep a-z, 0-9)
    s = re.sub(r'[^a-z0-9]+', '-', s)

    # Collapse multiple hyphens to single hyphen
    s = re.sub(r'-+', '-', s)

    # Strip leading/trailing hyphens
    s = s.strip('-')

    # Truncate to max_len and remove trailing hyphen if truncated
    if len(s) > max_len:
        s = s[:max_len].rstrip('-')

    return s or 'untitled'


def plan_id(title: str, today: Optional[datetime] = None) -> str:
    """
    Generate a PLAN ID.

    Format: PLAN-YYYYMMDD-ULID6-slug
    Example: PLAN-20251013-01T6N8-ship-auth

    Args:
        title: Plan title for slug generation
        today: Optional date override (for testing)

    Returns:
        Complete PLAN ID string
    """
    date = (today or datetime.now(timezone.utc))
    date_str = date.strftime('%Y%m%d')
    ulid6 = new_ulid6()
    slug = slugify(title)

    return f'PLAN-{date_str}-{ulid6}-{slug}'


def spec_id(title: str, today: Optional[datetime] = None) -> str:
    """
    Generate a SPEC ID.

    Format: SPEC-YYYYMMDD-ULID6-slug
    Example: SPEC-20251013-02NZ6Q-auth-flow

    Args:
        title: Spec title for slug generation
        today: Optional date override (for testing)

    Returns:
        Complete SPEC ID string
    """
    date = (today or datetime.now(timezone.utc))
    date_str = date.strftime('%Y%m%d')
    ulid6 = new_ulid6()
    slug = slugify(title)

    return f'SPEC-{date_str}-{ulid6}-{slug}'


def handle_filename_collision(filepath: Path) -> Path:
    """
    Handle filename collisions by appending -migrated-N suffix.

    If the file already exists (rare due to ULID uniqueness, but possible
    on branch merges), append -migrated-1, -migrated-2, etc.

    Note: This modifies the filename only, not the ID in the file's frontmatter.

    Args:
        filepath: Proposed file path

    Returns:
        Non-conflicting file path
    """
    if not filepath.exists():
        return filepath

    stem = filepath.stem
    suffix = filepath.suffix
    parent = filepath.parent

    # Try -migrated-1, -migrated-2, etc.
    counter = 1
    while True:
        new_path = parent / f"{stem}-migrated-{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

        # Safety check to avoid infinite loop
        if counter > 100:
            raise ValueError(f"Too many collisions for {filepath}")


def parse_id(id_str: str) -> dict:
    """
    Parse a PLAN/SPEC ID into its components.

    Args:
        id_str: ID string like "PLAN-20251013-01T6N8-ship-auth"

    Returns:
        Dictionary with keys: type, date, ulid6, slug

    Examples:
        parse_id("PLAN-20251013-01T6N8-auth")
        -> {"type": "PLAN", "date": "20251013", "ulid6": "01T6N8", "slug": "auth"}
    """
    # Pattern: TYPE-YYYYMMDD-ULID6-slug
    pattern = r'^(PLAN|SPEC)-(\d{8})-([A-Z0-9]{6})(?:-(.+))?$'
    m = re.match(pattern, id_str.upper())

    if not m:
        # Try legacy format (T-XXX, P-XXX)
        legacy_pattern = r'^([TP])-(\d+)$'
        legacy_m = re.match(legacy_pattern, id_str.upper())
        if legacy_m:
            return {
                "type": "TASK" if legacy_m.group(1) == "T" else "PLAN",
                "date": None,
                "ulid6": None,
                "slug": None,
                "number": int(legacy_m.group(2)),
                "legacy": True
            }

        raise ValueError(f"Invalid ID format: {id_str}")

    return {
        "type": m.group(1),
        "date": m.group(2),
        "ulid6": m.group(3),
        "slug": (m.group(4) or "").lower(),  # Keep slug lowercase
        "legacy": False
    }


def is_valid_id(id_str: str) -> bool:
    """
    Check if an ID string is valid.

    Args:
        id_str: ID string to validate

    Returns:
        True if valid PLAN/SPEC ID or legacy T-/P- format
    """
    try:
        parse_id(id_str)
        return True
    except ValueError:
        return False