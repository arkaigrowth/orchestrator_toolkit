"""
Tests for ULI and slug generation functionality.

This test suite covers:
- ULI generation and validation
- Slug generation and normalization
- Collision handling
- Unicode normalization
- Index management operations
"""

import pytest
import time
from pathlib import Path
from datetime import datetime
from tempfile import TemporaryDirectory

from orchestrator_toolkit.uli import (
    new_uli,
    validate_uli,
    extract_timestamp,
    extract_datetime,
    is_uli_older_than,
    uli_from_timestamp,
)
from orchestrator_toolkit.slug import (
    slugify,
    ensure_unique_slug,
    validate_slug,
    normalize_slug,
)
from orchestrator_toolkit.models.identifiers import SlugConfig, ULIIndexRecord
from orchestrator_toolkit.id_alloc import (
    dedupe_filename_with_slug,
    extract_slug_from_filename,
    parse_filename,
)
from orchestrator_toolkit.index_manager import IndexManager


class TestULI:
    """Test ULI generation and validation."""

    def test_new_uli_format(self):
        """Test that new_uli generates valid 26-character ULI."""
        uli = new_uli()
        assert len(uli) == 26
        assert validate_uli(uli)

    def test_uli_uniqueness(self):
        """Test that successive ULIs are unique."""
        ulis = [new_uli() for _ in range(100)]
        assert len(set(ulis)) == 100

    def test_validate_uli_valid(self):
        """Test validation of valid ULI."""
        uli = new_uli()
        assert validate_uli(uli)

    def test_validate_uli_invalid_length(self):
        """Test validation rejects wrong length."""
        assert not validate_uli("short")
        assert not validate_uli("0" * 25)
        assert not validate_uli("0" * 27)

    def test_validate_uli_invalid_characters(self):
        """Test validation rejects invalid characters."""
        # Contains I, L, O, U (excluded from Crockford base32)
        assert not validate_uli("01J9YAVWN3Z7D3X3Z5E7WFT6IL")
        assert not validate_uli("OOOOOOOOOOOOOOOOOOOOOOOOOO")
        assert not validate_uli("UUUUUUUUUUUUUUUUUUUUUUUUUU")

    def test_validate_uli_invalid_type(self):
        """Test validation rejects non-string types."""
        assert not validate_uli(None)
        assert not validate_uli(12345)
        assert not validate_uli([])

    def test_extract_timestamp(self):
        """Test timestamp extraction from ULI."""
        uli = new_uli()
        ts = extract_timestamp(uli)
        assert isinstance(ts, int)
        assert ts > 0
        # Should be recent (within last day)
        now_ms = int(time.time() * 1000)
        assert abs(now_ms - ts) < 86400000  # 1 day in ms

    def test_extract_datetime(self):
        """Test datetime extraction from ULI."""
        uli = new_uli()
        dt = extract_datetime(uli)
        assert isinstance(dt, datetime)
        # Should be recent (within last minute)
        # Make now timezone-aware to match ULI datetime (UTC)
        from datetime import timezone
        now = datetime.now(timezone.utc)
        assert abs((now - dt).total_seconds()) < 60

    def test_is_uli_older_than(self):
        """Test ULI comparison by timestamp."""
        uli1 = new_uli()
        time.sleep(0.002)  # Ensure different timestamp
        uli2 = new_uli()

        assert is_uli_older_than(uli1, uli2)
        assert not is_uli_older_than(uli2, uli1)

    def test_uli_from_timestamp(self):
        """Test creating ULI from specific timestamp."""
        timestamp_ms = 1634567890123
        uli = uli_from_timestamp(timestamp_ms)

        assert validate_uli(uli)
        assert extract_timestamp(uli) == timestamp_ms

    def test_uli_from_timestamp_with_randomness(self):
        """Test creating ULI with specific randomness."""
        timestamp_ms = 1634567890123
        randomness = b"1234567890"

        # Note: ulid-py doesn't easily support custom randomness
        # So we just test that it works with the timestamp
        uli = uli_from_timestamp(timestamp_ms, randomness)
        assert validate_uli(uli)
        # Timestamp should match (randomness is ignored for now)
        assert extract_timestamp(uli) == timestamp_ms


class TestSlug:
    """Test slug generation and validation."""

    def test_slugify_basic(self):
        """Test basic slug generation."""
        assert slugify("Fix Auth Bug") == "fix-auth-bug"
        assert slugify("Hello World") == "hello-world"

    def test_slugify_special_characters(self):
        """Test slug generation with special characters."""
        assert slugify("Fix Bug #42!") == "fix-bug-42"
        assert slugify("Hello @World & Friends") == "hello-world-friends"
        assert slugify("Test... Case???") == "test-case"

    def test_slugify_unicode(self):
        """Test slug generation with Unicode characters."""
        assert slugify("Café & Bar") == "cafe-bar"
        assert slugify("Über cool") == "uber-cool"
        assert slugify("Niño grande") == "nino-grande"

    def test_slugify_consecutive_hyphens(self):
        """Test slug collapses consecutive hyphens."""
        assert slugify("Fix   multiple   spaces") == "fix-multiple-spaces"
        assert slugify("Hello---World") == "hello-world"

    def test_slugify_max_length(self):
        """Test slug respects max length."""
        long_title = "This is a very long title that exceeds the maximum length"
        slug = slugify(long_title, max_len=20)
        assert len(slug) <= 20
        assert not slug.endswith("-")

    def test_slugify_empty_title(self):
        """Test slug generation with empty title."""
        with pytest.raises(ValueError):
            slugify("")
        with pytest.raises(ValueError):
            slugify("   ")

    def test_slugify_custom_config(self):
        """Test slug generation with custom config."""
        config = SlugConfig(
            separator="_",
            max_length=40,
        )
        assert slugify("Hello World", config=config) == "hello_world"

    def test_ensure_unique_slug_no_collision(self):
        """Test unique slug when no collision."""
        existing = {"other-slug", "another-slug"}
        slug = ensure_unique_slug("new-slug", existing)
        assert slug == "new-slug"

    def test_ensure_unique_slug_with_collision(self):
        """Test unique slug adds suffix on collision."""
        existing = {"fix-auth-bug", "fix-auth-bug-2"}
        slug = ensure_unique_slug("fix-auth-bug", existing)
        assert slug == "fix-auth-bug-3"

    def test_validate_slug_valid(self):
        """Test validation of valid slugs."""
        assert validate_slug("fix-auth-bug")
        assert validate_slug("hello-world")
        assert validate_slug("test123")

    def test_validate_slug_invalid(self):
        """Test validation of invalid slugs."""
        assert not validate_slug("")
        assert not validate_slug("-invalid-")
        assert not validate_slug("invalid-")
        assert not validate_slug("-invalid")
        assert not validate_slug("too--many--hyphens")
        assert not validate_slug("Invalid-Uppercase")

    def test_normalize_slug(self):
        """Test slug normalization."""
        assert normalize_slug("  Invalid-Slug--  ") == "invalid-slug"
        assert normalize_slug("CamelCaseSlug") == "camelcaseslug"


class TestIdAlloc:
    """Test ID allocation and filename generation."""

    def test_dedupe_filename_with_slug_no_collision(self):
        """Test filename generation without collision."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            filename, slug = dedupe_filename_with_slug(
                "T", "0042", "Fix Auth Bug", dir_path
            )
            assert filename == "T-0042--fix-auth-bug.md"
            assert slug == "fix-auth-bug"

    def test_dedupe_filename_with_slug_with_collision(self):
        """Test filename generation with collision."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)

            # Create existing file
            existing_file = dir_path / "T-0042--fix-auth-bug.md"
            existing_file.touch()

            filename, slug = dedupe_filename_with_slug(
                "T", "0042", "Fix Auth Bug", dir_path
            )
            assert filename == "T-0042--fix-auth-bug-2.md"
            assert slug == "fix-auth-bug-2"

    def test_extract_slug_from_filename(self):
        """Test slug extraction from filename."""
        assert extract_slug_from_filename("T-0042--fix-auth-bug.md") == "fix-auth-bug"
        assert extract_slug_from_filename("P-0007--migration-plan.md") == "migration-plan"
        assert extract_slug_from_filename("T-0042.md") is None
        assert extract_slug_from_filename("invalid.md") is None

    def test_parse_filename(self):
        """Test filename parsing into components."""
        result = parse_filename("T-0042--fix-auth-bug.md")
        assert result == {
            "prefix": "T",
            "numeric_id": "0042",
            "slug": "fix-auth-bug",
        }

        result = parse_filename("P-0007--migration-plan.md")
        assert result == {
            "prefix": "P",
            "numeric_id": "0007",
            "slug": "migration-plan",
        }

        assert parse_filename("invalid.md") is None
        assert parse_filename("T-0042.md") is None


class TestIndexManager:
    """Test index manager operations."""

    def test_index_manager_init(self):
        """Test index manager initialization."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path, auto_cache=False)
            assert manager.index_path == index_path

    def test_append_and_lookup_by_uli(self):
        """Test appending record and looking up by ULI."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path)

            record = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
                type="task",
                id="T-0042",
                slug="fix-auth-bug",
                path="tasks/T-0042--fix-auth-bug.md",
                title="Fix Auth Bug",
                created=datetime.now(),
            )

            manager.append(record)

            found = manager.lookup_by_uli("01J9YAVWN3Z7D3X3Z5E7WFT6A4")
            assert found is not None
            assert found.id == "T-0042"
            assert found.slug == "fix-auth-bug"

    def test_lookup_by_slug(self):
        """Test looking up records by slug."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path)

            record1 = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
                type="task",
                id="T-0042",
                slug="fix-auth-bug",
                path="tasks/T-0042--fix-auth-bug.md",
                title="Fix Auth Bug",
                created=datetime.now(),
            )

            record2 = ULIIndexRecord(
                uli="01J9YB5K8F2Q9P7X3M6N4R8S2T",
                type="plan",
                id="P-0007",
                slug="fix-auth-bug",
                path="plans/P-0007--fix-auth-bug.md",
                title="Fix Auth Bug Plan",
                created=datetime.now(),
            )

            manager.append(record1)
            manager.append(record2)

            found = manager.lookup_by_slug("fix-auth-bug")
            assert len(found) == 2

            tasks = manager.lookup_by_slug("fix-auth-bug", type_filter="task")
            assert len(tasks) == 1
            assert tasks[0].type == "task"

    def test_lookup_by_id(self):
        """Test looking up record by numeric ID."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path)

            record = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
                type="task",
                id="T-0042",
                slug="fix-auth-bug",
                path="tasks/T-0042--fix-auth-bug.md",
                title="Fix Auth Bug",
                created=datetime.now(),
            )

            manager.append(record)

            found = manager.lookup_by_id("T-0042")
            assert found is not None
            assert found.uli == "01J9YAVWN3Z7D3X3Z5E7WFT6A4"

    def test_refresh_cache(self):
        """Test cache refresh from file."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path)

            record = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
                type="task",
                id="T-0042",
                slug="fix-auth-bug",
                path="tasks/T-0042--fix-auth-bug.md",
                title="Fix Auth Bug",
                created=datetime.now(),
            )

            manager.append(record)

            # Create new manager instance and refresh cache
            manager2 = IndexManager(index_path, auto_cache=False)
            assert manager2.lookup_by_uli("01J9YAVWN3Z7D3X3Z5E7WFT6A4") is None

            manager2.refresh_cache()
            found = manager2.lookup_by_uli("01J9YAVWN3Z7D3X3Z5E7WFT6A4")
            assert found is not None

    def test_duplicate_uli_raises_error(self):
        """Test that duplicate ULI raises error."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path)

            record1 = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
                type="task",
                id="T-0042",
                slug="fix-auth-bug",
                path="tasks/T-0042--fix-auth-bug.md",
                title="Fix Auth Bug",
                created=datetime.now(),
            )

            record2 = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",  # Same ULI
                type="task",
                id="T-0043",
                slug="other-bug",
                path="tasks/T-0043--other-bug.md",
                title="Other Bug",
                created=datetime.now(),
            )

            manager.append(record1)

            with pytest.raises(ValueError, match="ULI .* already exists"):
                manager.append(record2)

    def test_get_all_records(self):
        """Test getting all records from cache."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path)

            record1 = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
                type="task",
                id="T-0042",
                slug="fix-auth-bug",
                path="tasks/T-0042--fix-auth-bug.md",
                title="Fix Auth Bug",
                created=datetime.now(),
            )

            record2 = ULIIndexRecord(
                uli="01J9YB5K8F2Q9P7X3M6N4R8S2T",
                type="plan",
                id="P-0007",
                slug="migration-plan",
                path="plans/P-0007--migration-plan.md",
                title="Migration Plan",
                created=datetime.now(),
            )

            manager.append(record1)
            manager.append(record2)

            all_records = manager.get_all_records()
            assert len(all_records) == 2

    def test_validate_index(self):
        """Test index validation."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "uli_index.jsonl"
            manager = IndexManager(index_path)

            record = ULIIndexRecord(
                uli="01J9YAVWN3Z7D3X3Z5E7WFT6A4",
                type="task",
                id="T-0042",
                slug="fix-auth-bug",
                path="tasks/T-0042--fix-auth-bug.md",
                title="Fix Auth Bug",
                created=datetime.now(),
            )

            manager.append(record)

            errors = manager.validate_index()
            assert len(errors) == 0
