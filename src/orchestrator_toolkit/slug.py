"""
Slug generation and normalization utilities.

This module provides functions for converting human-readable titles
into URL-safe slugs with configurable behavior.

Slug Properties:
- Lowercase alphanumeric with hyphens
- No consecutive hyphens
- No leading/trailing hyphens
- Maximum 60 characters (configurable)
- Unicode normalization for international characters

Example: "Fix Auth Bug!" → "fix-auth-bug"
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from orchestrator_toolkit.models.identifiers import SlugConfig


def slugify(
    title: str,
    max_len: Optional[int] = None,
    config: Optional[SlugConfig] = None,
) -> str:
    """
    Convert title to URL-safe slug.

    Process:
    1. Unicode normalization (NFKD)
    2. ASCII conversion (optional, based on config)
    3. Lowercase conversion
    4. Non-alphanumeric replacement with separator
    5. Consecutive separator collapse
    6. Leading/trailing separator removal
    7. Length truncation

    Args:
        title: Human-readable title to convert
        max_len: Maximum slug length (overrides config)
        config: SlugConfig for customization (uses defaults if None)

    Returns:
        URL-safe slug string

    Raises:
        ValueError: If title is empty or results in empty slug

    Example:
        >>> slugify("Fix Auth Bug!")
        'fix-auth-bug'
        >>> slugify("Hello   World", max_len=10)
        'hello-worl'
        >>> slugify("Café & Bar", config=SlugConfig(remove_unicode=False))
        'café-bar'
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    # Use default config if not provided
    if config is None:
        config = SlugConfig()

    # Use provided max_len or config default
    length_limit = max_len if max_len is not None else config.max_length

    # Step 1: Unicode normalization
    s = unicodedata.normalize("NFKD", title)

    # Step 2: ASCII conversion (if configured)
    if config.remove_unicode:
        s = s.encode("ascii", "ignore").decode("ascii")

    # Step 3: Lowercase conversion (if configured)
    if config.lowercase:
        s = s.lower()

    # Step 4: Replace non-alphanumeric with separator
    # Keep only alphanumeric and separator characters
    pattern = r"[^a-z0-9]+" if config.lowercase else r"[^a-zA-Z0-9]+"
    s = re.sub(pattern, config.separator, s)

    # Step 5: Collapse consecutive separators
    s = re.sub(f"{re.escape(config.separator)}{{2,}}", config.separator, s)

    # Step 6: Remove leading/trailing separators
    s = s.strip(config.separator)

    # Step 7: Truncate to max length
    if len(s) > length_limit:
        s = s[:length_limit].rstrip(config.separator)

    if not s:
        raise ValueError(f"Title '{title}' results in empty slug")

    return s


def ensure_unique_slug(
    base_slug: str,
    existing_slugs: set[str],
    config: Optional[SlugConfig] = None,
) -> str:
    """
    Generate unique slug by adding numeric suffix if collision detected.

    Process:
    - Check if base_slug exists in existing_slugs
    - If not, return base_slug
    - If yes, append suffix (-2, -3, etc.) until unique

    Args:
        base_slug: Initial slug to check
        existing_slugs: Set of already-used slugs
        config: SlugConfig for suffix format (uses defaults if None)

    Returns:
        Unique slug string (original or with suffix)

    Example:
        >>> existing = {"fix-auth-bug", "fix-auth-bug-2"}
        >>> ensure_unique_slug("fix-auth-bug", existing)
        'fix-auth-bug-3'
        >>> ensure_unique_slug("new-task", existing)
        'new-task'
    """
    if config is None:
        config = SlugConfig()

    if base_slug not in existing_slugs:
        return base_slug

    # Try successive numbers until we find an unused one
    counter = 2
    while True:
        candidate = base_slug + config.collision_suffix_format.format(n=counter)
        if candidate not in existing_slugs:
            return candidate
        counter += 1


def validate_slug(slug: str, config: Optional[SlugConfig] = None) -> bool:
    """
    Validate slug format against configuration rules.

    Checks:
    - Not empty
    - Within max length
    - No leading/trailing separator
    - No consecutive separators
    - Only valid characters (alphanumeric + separator)

    Args:
        slug: Slug string to validate
        config: SlugConfig for validation rules (uses defaults if None)

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_slug("fix-auth-bug")
        True
        >>> validate_slug("-invalid-")
        False
        >>> validate_slug("too--many--hyphens")
        False
    """
    if config is None:
        config = SlugConfig()

    if not slug:
        return False

    if len(slug) > config.max_length:
        return False

    # Check for leading/trailing separator
    if slug.startswith(config.separator) or slug.endswith(config.separator):
        return False

    # Check for consecutive separators
    if f"{config.separator}{config.separator}" in slug:
        return False

    # Check character set
    pattern = r"^[a-z0-9" + re.escape(config.separator) + r"]+$"
    if not re.match(pattern, slug):
        return False

    return True


def normalize_slug(slug: str, config: Optional[SlugConfig] = None) -> str:
    """
    Normalize existing slug to meet format requirements.

    Useful for cleaning up manually-created slugs or migrating
    from different slug formats.

    Args:
        slug: Existing slug to normalize
        config: SlugConfig for normalization rules

    Returns:
        Normalized slug string

    Raises:
        ValueError: If slug cannot be normalized

    Example:
        >>> normalize_slug("  Invalid-Slug--  ")
        'invalid-slug'
        >>> normalize_slug("CamelCaseSlug")
        'camelcaseslug'
    """
    if config is None:
        config = SlugConfig()

    # Apply same process as slugify
    return slugify(slug, config=config)
