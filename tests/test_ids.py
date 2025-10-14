"""
Tests for ID generation system
"""
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestrator_toolkit.ids import (
    new_ulid6, slugify, plan_id, spec_id,
    handle_filename_collision, parse_id, is_valid_id
)


class TestULID6:
    """Test ULID6 generation."""

    def test_ulid6_length(self):
        """ULID6 should be exactly 6 characters."""
        ulid6 = new_ulid6()
        assert len(ulid6) == 6

    def test_ulid6_uppercase(self):
        """ULID6 should be uppercase."""
        ulid6 = new_ulid6()
        assert ulid6.isupper()

    def test_ulid6_uniqueness(self):
        """Multiple ULID6s should be unique (with high probability)."""
        import time
        ulids = []
        for _ in range(10):
            ulids.append(new_ulid6())
            time.sleep(0.001)  # Small delay to ensure different timestamps
        # All should be unique with delays
        assert len(set(ulids)) == 10

    def test_ulid6_format(self):
        """ULID6 should only contain Crockford base32 characters."""
        ulid6 = new_ulid6()
        # Crockford base32 alphabet (uppercase)
        valid_chars = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
        assert all(c in valid_chars for c in ulid6)


class TestSlugify:
    """Test slug generation."""

    def test_basic_slugify(self):
        """Basic text becomes lowercase hyphenated."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Auth System") == "auth-system"

    def test_special_characters(self):
        """Special characters become hyphens."""
        assert slugify("Hello, World!") == "hello-world"
        assert slugify("Auth 2.0 System") == "auth-2-0-system"
        assert slugify("C++ Code") == "c-code"

    def test_multiple_spaces(self):
        """Multiple spaces collapse to single hyphen."""
        assert slugify("Hello    World") == "hello-world"
        assert slugify("Too  Many   Spaces") == "too-many-spaces"

    def test_leading_trailing(self):
        """Leading/trailing special chars are removed."""
        assert slugify("...Hello World...") == "hello-world"
        assert slugify("  Trimmed  ") == "trimmed"

    def test_empty_input(self):
        """Empty input returns 'untitled'."""
        assert slugify("") == "untitled"
        assert slugify(None) == "untitled"
        assert slugify("   ") == "untitled"

    def test_max_length(self):
        """Slug is truncated to max length."""
        long_title = "This is a very long title that should be truncated"
        slug = slugify(long_title, max_len=20)
        assert len(slug) <= 20
        assert slug == "this-is-a-very-long"

    def test_max_length_word_boundary(self):
        """Truncation happens at word boundary when possible."""
        title = "authentication-system-implementation"
        slug = slugify(title, max_len=15)
        assert slug == "authentication"  # Breaks at word boundary

    def test_numbers(self):
        """Numbers are preserved."""
        assert slugify("Version 123") == "version-123"
        assert slugify("2024 Report") == "2024-report"

    def test_unicode(self):
        """Unicode characters are replaced with hyphens."""
        assert slugify("Café résumé") == "caf-r-sum"
        assert slugify("Hello 世界") == "hello"

    def test_all_special(self):
        """Input with only special chars returns 'untitled'."""
        assert slugify("!!!@@@###") == "untitled"
        assert slugify("---") == "untitled"


class TestPlanID:
    """Test PLAN ID generation."""

    def test_plan_id_format(self):
        """PLAN ID has correct format."""
        test_date = datetime(2025, 10, 13, tzinfo=timezone.utc)
        with patch('orchestrator_toolkit.ids.new_ulid6', return_value='01T6N8'):
            pid = plan_id("Ship Auth", today=test_date)
            assert pid.startswith("PLAN-20251013-01T6N8-ship-auth")

    def test_plan_id_with_empty_title(self):
        """Empty title results in 'untitled' slug."""
        test_date = datetime(2025, 10, 13, tzinfo=timezone.utc)
        with patch('orchestrator_toolkit.ids.new_ulid6', return_value='01T6N8'):
            pid = plan_id("", today=test_date)
            assert pid == "PLAN-20251013-01T6N8-untitled"

    def test_plan_id_current_date(self):
        """Without date override, uses current date."""
        pid = plan_id("Test Plan")
        # Should have today's date in YYYYMMDD format
        today = datetime.now(timezone.utc).strftime('%Y%m%d')
        assert f"PLAN-{today}" in pid


class TestSpecID:
    """Test SPEC ID generation."""

    def test_spec_id_format(self):
        """SPEC ID has correct format."""
        test_date = datetime(2025, 10, 13, tzinfo=timezone.utc)
        with patch('orchestrator_toolkit.ids.new_ulid6', return_value='02NZ6Q'):
            sid = spec_id("Auth Flow", today=test_date)
            assert sid == "SPEC-20251013-02NZ6Q-auth-flow"

    def test_spec_id_different_from_plan(self):
        """SPEC ID uses SPEC prefix."""
        test_date = datetime(2025, 10, 13, tzinfo=timezone.utc)
        with patch('orchestrator_toolkit.ids.new_ulid6', return_value='02NZ6Q'):
            sid = spec_id("Same Title", today=test_date)
            assert sid.startswith("SPEC-")


class TestHandleCollision:
    """Test filename collision handling."""

    def test_no_collision(self, tmp_path):
        """No collision returns original path."""
        filepath = tmp_path / "PLAN-20251013-01T6N8-auth.md"
        result = handle_filename_collision(filepath)
        assert result == filepath

    def test_single_collision(self, tmp_path):
        """Single collision adds -migrated-1."""
        filepath = tmp_path / "PLAN-20251013-01T6N8-auth.md"
        filepath.touch()  # Create the file

        result = handle_filename_collision(filepath)
        assert result == tmp_path / "PLAN-20251013-01T6N8-auth-migrated-1.md"

    def test_multiple_collisions(self, tmp_path):
        """Multiple collisions increment counter."""
        base = tmp_path / "PLAN-20251013-01T6N8-auth.md"
        base.touch()
        (tmp_path / "PLAN-20251013-01T6N8-auth-migrated-1.md").touch()
        (tmp_path / "PLAN-20251013-01T6N8-auth-migrated-2.md").touch()

        result = handle_filename_collision(base)
        assert result == tmp_path / "PLAN-20251013-01T6N8-auth-migrated-3.md"


class TestParseID:
    """Test ID parsing."""

    def test_parse_plan_id(self):
        """Parse valid PLAN ID."""
        result = parse_id("PLAN-20251013-01T6N8-ship-auth")
        assert result == {
            "type": "PLAN",
            "date": "20251013",
            "ulid6": "01T6N8",
            "slug": "ship-auth",
            "legacy": False
        }

    def test_parse_spec_id(self):
        """Parse valid SPEC ID."""
        result = parse_id("SPEC-20251013-02NZ6Q-auth-flow")
        assert result == {
            "type": "SPEC",
            "date": "20251013",
            "ulid6": "02NZ6Q",
            "slug": "auth-flow",
            "legacy": False
        }

    def test_parse_no_slug(self):
        """Parse ID without slug."""
        result = parse_id("PLAN-20251013-01T6N8")
        assert result["slug"] == ""

    def test_parse_legacy_task(self):
        """Parse legacy T-XXX format."""
        result = parse_id("T-001")
        assert result == {
            "type": "TASK",
            "date": None,
            "ulid6": None,
            "slug": None,
            "number": 1,
            "legacy": True
        }

    def test_parse_legacy_plan(self):
        """Parse legacy P-XXX format."""
        result = parse_id("P-042")
        assert result == {
            "type": "PLAN",
            "date": None,
            "ulid6": None,
            "slug": None,
            "number": 42,
            "legacy": True
        }

    def test_parse_invalid(self):
        """Invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid ID format"):
            parse_id("invalid-id")

        with pytest.raises(ValueError):
            parse_id("UNKNOWN-20251013-01T6N8")

    def test_parse_case_insensitive(self):
        """Parsing is case-insensitive."""
        result = parse_id("plan-20251013-01t6n8-auth")
        assert result["type"] == "PLAN"
        assert result["ulid6"] == "01T6N8"  # Normalized to uppercase


class TestIsValidID:
    """Test ID validation."""

    def test_valid_ids(self):
        """Valid IDs return True."""
        assert is_valid_id("PLAN-20251013-01T6N8-auth")
        assert is_valid_id("SPEC-20251013-02NZ6Q-flow")
        assert is_valid_id("PLAN-20251013-01T6N8")  # No slug
        assert is_valid_id("T-001")  # Legacy
        assert is_valid_id("P-999")  # Legacy

    def test_invalid_ids(self):
        """Invalid IDs return False."""
        assert not is_valid_id("invalid")
        assert not is_valid_id("TASK-20251013-01T6N8")  # Wrong type
        assert not is_valid_id("PLAN-2025-01T6N8")  # Wrong date format
        assert not is_valid_id("PLAN-20251013-SHORT")  # ULID too short
        assert not is_valid_id("X-001")  # Wrong legacy prefix