"""
ID allocation utilities for generating unique task and plan identifiers.

This module provides functions for:
- Numeric ID generation (T-0001, P-0002, etc.)
- Slug-based filename deduplication
- Collision detection and resolution

All functions avoid global counter files to prevent merge conflicts
in collaborative environments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from orchestrator_toolkit.slug import ensure_unique_slug, slugify
from orchestrator_toolkit.models.identifiers import SlugConfig


def next_numeric(prefix: str, dir_: Path) -> str:
    """
    Scans dir_ for files named like 'T-0001.md' or 'P-0123.md'
    and returns the next zero-padded number as a 4-digit string.

    This avoids global counter files that can cause merge conflicts
    and instead derives the next ID from existing files in the directory.

    Args:
        prefix: File prefix (e.g., "T", "P")
        dir_: Directory to scan for existing files

    Returns:
        4-digit zero-padded numeric ID string

    Example:
        >>> from pathlib import Path
        >>> next_numeric("T", Path("tasks"))
        '0042'
    """
    hi = 0
    if dir_.is_dir():
        for p in dir_.glob(f"{prefix}-*.md"):
            try:
                # Extract the numeric part after the prefix
                num = int(p.stem.split("-")[1])
                hi = max(hi, num)
            except Exception:
                # Ignore files that don't match the expected pattern
                continue
    return f"{hi + 1:04d}"


def dedupe_filename_with_slug(
    prefix: str,
    numeric_id: str,
    title: str,
    dir_: Path,
    config: Optional[SlugConfig] = None,
) -> tuple[str, str]:
    """
    Generate unique filename with format: {prefix}-{numeric_id}--{slug}.md

    This function:
    1. Generates slug from title
    2. Checks for existing files with same slug
    3. Adds numeric suffix if collision detected
    4. Returns both filename and slug

    Args:
        prefix: File prefix (e.g., "T", "P")
        numeric_id: 4-digit numeric ID (e.g., "0042")
        title: Human-readable title for slug generation
        dir_: Directory to check for existing files
        config: SlugConfig for customization (uses defaults if None)

    Returns:
        Tuple of (filename, slug)
        - filename: Complete filename with extension (e.g., "T-0042--fix-auth-bug.md")
        - slug: Generated slug (e.g., "fix-auth-bug")

    Example:
        >>> from pathlib import Path
        >>> dedupe_filename_with_slug("T", "0042", "Fix Auth Bug", Path("tasks"))
        ('T-0042--fix-auth-bug.md', 'fix-auth-bug')

        >>> # If T-0042--fix-auth-bug.md exists, returns:
        >>> dedupe_filename_with_slug("T", "0042", "Fix Auth Bug", Path("tasks"))
        ('T-0042--fix-auth-bug-2.md', 'fix-auth-bug-2')
    """
    # Generate base slug from title
    base_slug = slugify(title, config=config)

    # Find all existing slugs for this numeric ID
    # Pattern: {prefix}-{numeric_id}--*.md
    pattern = f"{prefix}-{numeric_id}--*.md"
    existing_slugs = set()

    if dir_.is_dir():
        for p in dir_.glob(pattern):
            try:
                # Extract slug from filename: T-0042--fix-auth-bug.md -> fix-auth-bug
                stem = p.stem  # Remove .md
                parts = stem.split("--", 1)
                if len(parts) == 2:
                    existing_slugs.add(parts[1])
            except Exception:
                # Ignore files that don't match expected pattern
                continue

    # Ensure slug is unique
    unique_slug = ensure_unique_slug(base_slug, existing_slugs, config=config)

    # Construct filename
    filename = f"{prefix}-{numeric_id}--{unique_slug}.md"

    return filename, unique_slug


def extract_slug_from_filename(filename: str) -> Optional[str]:
    """
    Extract slug from filename with format: {prefix}-{numeric_id}--{slug}.md

    Args:
        filename: Filename to parse

    Returns:
        Slug string if format matches, None otherwise

    Example:
        >>> extract_slug_from_filename("T-0042--fix-auth-bug.md")
        'fix-auth-bug'
        >>> extract_slug_from_filename("T-0042.md")
        None
    """
    # Remove .md extension if present
    stem = filename[:-3] if filename.endswith(".md") else filename

    # Split on double hyphen
    parts = stem.split("--", 1)
    if len(parts) != 2:
        return None

    return parts[1]


def parse_filename(filename: str) -> Optional[dict[str, str]]:
    """
    Parse filename into components.

    Args:
        filename: Filename to parse

    Returns:
        Dict with keys: prefix, numeric_id, slug
        Returns None if format doesn't match

    Example:
        >>> parse_filename("T-0042--fix-auth-bug.md")
        {'prefix': 'T', 'numeric_id': '0042', 'slug': 'fix-auth-bug'}
        >>> parse_filename("invalid.md")
        None
    """
    # Remove .md extension if present
    stem = filename[:-3] if filename.endswith(".md") else filename

    # Split on double hyphen
    parts = stem.split("--", 1)
    if len(parts) != 2:
        return None

    # Parse first part: T-0042
    id_parts = parts[0].split("-", 1)
    if len(id_parts) != 2:
        return None

    return {
        "prefix": id_parts[0],
        "numeric_id": id_parts[1],
        "slug": parts[1],
    }