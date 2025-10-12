"""
Index manager for ULI-based task and plan lookup.

This module provides thread-safe index management for fast lookups
of tasks and plans by ULI, slug, or numeric ID.

Features:
- Atomic append operations with file locking
- Fast in-memory lookup with caching
- Index rebuilding from filesystem
- Collision detection and validation

Storage format: claude/uli_index.jsonl (one JSON record per line)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Literal
from datetime import datetime
from collections import defaultdict

try:
    from filelock import FileLock, Timeout
except ImportError:
    raise ImportError(
        "filelock is required for index management. "
        "Install with: pip install filelock"
    )

from orchestrator_toolkit.models.identifiers import ULIIndexRecord


class IndexManager:
    """
    Thread-safe manager for ULI index operations.

    Provides:
    - Fast lookups by ULI, slug, or numeric ID
    - Atomic append with file locking
    - In-memory caching for performance
    - Index rebuilding and validation

    Usage:
        >>> manager = IndexManager(Path("claude/uli_index.jsonl"))
        >>> record = ULIIndexRecord(
        ...     uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
        ...     type="task",
        ...     id="T-0042",
        ...     slug="fix-auth-bug",
        ...     path="tasks/T-0042--fix-auth-bug.md",
        ...     title="Fix Auth Bug",
        ...     created=datetime.now()
        ... )
        >>> manager.append(record)
        >>> found = manager.lookup_by_uli("01J9YAVWN3Z7D3X3Z5E7WFT6A4")
    """

    def __init__(
        self,
        index_path: Path,
        lock_timeout: float = 10.0,
        auto_cache: bool = True,
    ):
        """
        Initialize index manager.

        Args:
            index_path: Path to uli_index.jsonl file
            lock_timeout: Maximum seconds to wait for lock (default 10)
            auto_cache: Load index into memory on init (default True)
        """
        self.index_path = index_path
        self.lock_path = index_path.with_suffix(".lock")
        self.lock_timeout = lock_timeout

        # In-memory caches for fast lookups
        self._cache_by_uli: dict[str, ULIIndexRecord] = {}
        self._cache_by_slug: dict[str, list[ULIIndexRecord]] = defaultdict(list)
        self._cache_by_id: dict[str, ULIIndexRecord] = {}

        # Load cache if requested
        if auto_cache:
            self.refresh_cache()

    def append(self, record: ULIIndexRecord) -> None:
        """
        Atomically append record to index with file locking.

        Args:
            record: ULIIndexRecord to append

        Raises:
            Timeout: If lock cannot be acquired within timeout
            ValueError: If record conflicts with existing entries

        Example:
            >>> manager.append(record)
        """
        # Validate no conflicts
        if self.lookup_by_uli(record.uli) is not None:
            raise ValueError(f"ULI {record.uli} already exists in index")
        if self.lookup_by_id(record.id) is not None:
            raise ValueError(f"ID {record.id} already exists in index")

        # Acquire lock and append
        lock = FileLock(self.lock_path, timeout=self.lock_timeout)

        try:
            with lock:
                # Ensure parent directory exists
                self.index_path.parent.mkdir(parents=True, exist_ok=True)

                # Append record as JSON line
                with open(self.index_path, "a", encoding="utf-8") as f:
                    json_line = record.model_dump_json() + "\n"
                    f.write(json_line)

                # Update cache
                self._add_to_cache(record)

        except Timeout as e:
            raise Timeout(
                f"Could not acquire lock for {self.index_path} "
                f"within {self.lock_timeout} seconds"
            ) from e

    def lookup_by_uli(self, uli: str) -> Optional[ULIIndexRecord]:
        """
        Lookup record by ULI.

        Args:
            uli: 26-character ULI string

        Returns:
            ULIIndexRecord if found, None otherwise

        Example:
            >>> record = manager.lookup_by_uli("01J9YAVWN3Z7D3X3Z5E7WFT6A4")
        """
        return self._cache_by_uli.get(uli)

    def lookup_by_slug(
        self,
        slug: str,
        type_filter: Optional[Literal["task", "plan"]] = None,
    ) -> list[ULIIndexRecord]:
        """
        Lookup records by slug.

        Multiple records can have the same slug if they are different types
        or have different numeric IDs.

        Args:
            slug: Slug to search for
            type_filter: Optional filter by type ("task" or "plan")

        Returns:
            List of matching ULIIndexRecord objects (may be empty)

        Example:
            >>> records = manager.lookup_by_slug("fix-auth-bug")
            >>> task_records = manager.lookup_by_slug("fix-auth-bug", type_filter="task")
        """
        records = self._cache_by_slug.get(slug, [])

        if type_filter:
            records = [r for r in records if r.type == type_filter]

        return records

    def lookup_by_id(self, id: str) -> Optional[ULIIndexRecord]:
        """
        Lookup record by numeric ID (T-XXXX or P-XXXX).

        Args:
            id: Numeric ID string

        Returns:
            ULIIndexRecord if found, None otherwise

        Example:
            >>> record = manager.lookup_by_id("T-0042")
        """
        return self._cache_by_id.get(id)

    def refresh_cache(self) -> None:
        """
        Rebuild in-memory cache from index file.

        Useful for:
        - Initial load
        - Recovering from cache corruption
        - Syncing after external modifications

        Example:
            >>> manager.refresh_cache()
        """
        # Clear existing caches
        self._cache_by_uli.clear()
        self._cache_by_slug.clear()
        self._cache_by_id.clear()

        # Reload from file if it exists
        if not self.index_path.exists():
            return

        with open(self.index_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    record = ULIIndexRecord(**data)
                    self._add_to_cache(record)

                except (json.JSONDecodeError, ValueError) as e:
                    # Log warning but continue processing
                    print(
                        f"Warning: Invalid record at line {line_num} "
                        f"in {self.index_path}: {e}"
                    )
                    continue

    def rebuild_from_filesystem(
        self,
        tasks_dir: Path,
        plans_dir: Path,
    ) -> tuple[int, int]:
        """
        Rebuild index from filesystem by scanning task/plan directories.

        This is useful for:
        - Initial index creation
        - Recovery from index corruption
        - Migration from old format

        Args:
            tasks_dir: Directory containing task files
            plans_dir: Directory containing plan files

        Returns:
            Tuple of (tasks_indexed, plans_indexed)

        Example:
            >>> tasks, plans = manager.rebuild_from_filesystem(
            ...     Path("tasks"),
            ...     Path("plans")
            ... )
            >>> print(f"Indexed {tasks} tasks and {plans} plans")
        """
        from orchestrator_toolkit.id_alloc import parse_filename
        from orchestrator_toolkit.uli import new_uli

        # Clear existing index
        if self.index_path.exists():
            self.index_path.unlink()

        self._cache_by_uli.clear()
        self._cache_by_slug.clear()
        self._cache_by_id.clear()

        task_count = 0
        plan_count = 0

        # Index tasks
        if tasks_dir.exists():
            for task_file in sorted(tasks_dir.glob("T-*.md")):
                parsed = parse_filename(task_file.name)
                if not parsed:
                    continue

                # Read front matter to get title
                title = self._extract_title_from_file(task_file)
                if not title:
                    title = parsed["slug"].replace("-", " ").title()

                record = ULIIndexRecord(
                    uli=new_uli(),
                    type="task",
                    id=f"{parsed['prefix']}-{parsed['numeric_id']}",
                    slug=parsed["slug"],
                    path=str(task_file.relative_to(task_file.parent.parent)),
                    title=title,
                    created=datetime.fromtimestamp(task_file.stat().st_ctime),
                )

                self.append(record)
                task_count += 1

        # Index plans
        if plans_dir.exists():
            for plan_file in sorted(plans_dir.glob("P-*.md")):
                parsed = parse_filename(plan_file.name)
                if not parsed:
                    continue

                # Read front matter to get title
                title = self._extract_title_from_file(plan_file)
                if not title:
                    title = parsed["slug"].replace("-", " ").title()

                record = ULIIndexRecord(
                    uli=new_uli(),
                    type="plan",
                    id=f"{parsed['prefix']}-{parsed['numeric_id']}",
                    slug=parsed["slug"],
                    path=str(plan_file.relative_to(plan_file.parent.parent)),
                    title=title,
                    created=datetime.fromtimestamp(plan_file.stat().st_ctime),
                )

                self.append(record)
                plan_count += 1

        return task_count, plan_count

    def _add_to_cache(self, record: ULIIndexRecord) -> None:
        """Add record to all cache indexes."""
        self._cache_by_uli[record.uli] = record
        self._cache_by_slug[record.slug].append(record)
        self._cache_by_id[record.id] = record

    def _extract_title_from_file(self, file_path: Path) -> Optional[str]:
        """
        Extract title from YAML front matter.

        Args:
            file_path: Path to markdown file

        Returns:
            Title string if found, None otherwise
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple YAML front matter parser
            if not content.startswith("---"):
                return None

            # Find end of front matter
            end_marker = content.find("---", 3)
            if end_marker == -1:
                return None

            front_matter = content[3:end_marker]

            # Look for title line
            for line in front_matter.split("\n"):
                line = line.strip()
                if line.startswith("title:"):
                    title = line[6:].strip()
                    # Remove quotes if present
                    if title.startswith('"') and title.endswith('"'):
                        title = title[1:-1]
                    elif title.startswith("'") and title.endswith("'"):
                        title = title[1:-1]
                    return title

            return None

        except Exception:
            return None

    def get_all_records(self) -> list[ULIIndexRecord]:
        """
        Get all records from cache.

        Returns:
            List of all ULIIndexRecord objects

        Example:
            >>> all_records = manager.get_all_records()
            >>> print(f"Total records: {len(all_records)}")
        """
        return list(self._cache_by_uli.values())

    def validate_index(self) -> list[str]:
        """
        Validate index for duplicates and inconsistencies.

        Returns:
            List of validation error messages (empty if valid)

        Example:
            >>> errors = manager.validate_index()
            >>> if errors:
            ...     for error in errors:
            ...         print(f"Error: {error}")
        """
        errors = []

        # Check for duplicate ULIs
        uli_counts: dict[str, int] = defaultdict(int)
        for record in self._cache_by_uli.values():
            uli_counts[record.uli] += 1

        for uli, count in uli_counts.items():
            if count > 1:
                errors.append(f"Duplicate ULI: {uli} appears {count} times")

        # Check for duplicate IDs
        id_counts: dict[str, int] = defaultdict(int)
        for record in self._cache_by_id.values():
            id_counts[record.id] += 1

        for id, count in id_counts.items():
            if count > 1:
                errors.append(f"Duplicate ID: {id} appears {count} times")

        return errors
