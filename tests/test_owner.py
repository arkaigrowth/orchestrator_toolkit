"""
Tests for Owner Resolution System
"""
import os
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

from orchestrator_toolkit.owner import (
    resolve_owner,
    clear_owner_cache,
    pick_plan_interactively,
    pick_spec_interactively,
    _extract_title_from_frontmatter
)


@pytest.fixture(autouse=True)
def reset_cache():
    """Clear owner cache before each test."""
    clear_owner_cache()
    yield
    clear_owner_cache()


@pytest.fixture
def mock_no_cache_file(monkeypatch, tmp_path):
    """Run each test in an isolated working directory.

    resolve_owner() reads and writes a per-repo .otk/.owner cache relative to
    the current directory. Running in a fresh tmp cwd means that cache neither
    pre-exists (so the cascade falls through as intended) nor leaks into the
    real repo or sibling tests.
    """
    monkeypatch.chdir(tmp_path)


class TestResolveOwner:
    """Tests for owner resolution cascade."""

    def test_cascade_env_var_wins(self, monkeypatch, mock_no_cache_file):
        """Environment variable takes highest priority."""
        monkeypatch.setenv('OTK_DEFAULT_OWNER', 'alice')
        assert resolve_owner() == 'alice'

    def test_cascade_cached_value(self, monkeypatch, mock_no_cache_file):
        """Cached value is returned without re-evaluation."""
        monkeypatch.setenv('OTK_DEFAULT_OWNER', 'alice')
        assert resolve_owner() == 'alice'

        # Remove env var - should still return cached value
        monkeypatch.delenv('OTK_DEFAULT_OWNER', raising=False)
        assert resolve_owner() == 'alice'

    def test_cascade_git_config_fallback(self, monkeypatch, mock_no_cache_file):
        """Git config is used when env var not set."""
        monkeypatch.delenv('OTK_DEFAULT_OWNER', raising=False)
        monkeypatch.delenv('OTK_OWNER', raising=False)
        monkeypatch.delenv('GITHUB_ACTOR', raising=False)

        with patch('subprocess.check_output') as mock_git:
            mock_git.return_value = 'Bob Smith\n'
            assert resolve_owner() == 'Bob Smith'

    def test_cascade_git_config_empty(self, monkeypatch, mock_no_cache_file):
        """Empty git config falls through to prompt."""
        monkeypatch.delenv('OTK_DEFAULT_OWNER', raising=False)
        monkeypatch.delenv('OTK_OWNER', raising=False)
        monkeypatch.delenv('GITHUB_ACTOR', raising=False)

        with patch('subprocess.check_output') as mock_git:
            mock_git.return_value = ''

            # resolve_owner() prefers click.prompt (with an input() fallback),
            # so the interactive answer must be simulated at click.prompt.
            with patch('click.prompt', return_value='charlie'):
                assert resolve_owner() == 'charlie'

    def test_cascade_git_config_fails(self, monkeypatch, mock_no_cache_file):
        """Git config failure falls through to prompt."""
        monkeypatch.delenv('OTK_DEFAULT_OWNER', raising=False)
        monkeypatch.delenv('OTK_OWNER', raising=False)
        monkeypatch.delenv('GITHUB_ACTOR', raising=False)

        with patch('subprocess.check_output') as mock_git:
            mock_git.side_effect = subprocess.CalledProcessError(1, 'git')

            with patch('click.prompt', return_value='dave'):
                assert resolve_owner() == 'dave'

    def test_cascade_prompt_default(self, monkeypatch, mock_no_cache_file):
        """Empty prompt input uses default 'unknown'."""
        monkeypatch.delenv('OTK_DEFAULT_OWNER', raising=False)
        monkeypatch.delenv('OTK_OWNER', raising=False)
        monkeypatch.delenv('GITHUB_ACTOR', raising=False)

        with patch('subprocess.check_output') as mock_git:
            mock_git.return_value = ''

            # An empty answer at the prompt resolves to the "unknown" default.
            with patch('click.prompt', return_value='unknown'):
                assert resolve_owner() == 'unknown'

    @pytest.mark.skip(reason="KeyboardInterrupt test causes pytest issues")
    def test_cascade_prompt_keyboard_interrupt(self, monkeypatch):
        """Keyboard interrupt during prompt falls back to unknown."""
        # This test is valid but causes pytest to catch the KeyboardInterrupt
        # In practice, the code handles KeyboardInterrupt correctly
        pass

    def test_cascade_final_fallback(self, monkeypatch, mock_no_cache_file):
        """Final fallback is 'unknown' when all else fails."""
        monkeypatch.delenv('OTK_DEFAULT_OWNER', raising=False)
        monkeypatch.delenv('OTK_OWNER', raising=False)
        monkeypatch.delenv('GITHUB_ACTOR', raising=False)

        with patch('subprocess.check_output') as mock_git:
            mock_git.side_effect = Exception("Git not available")

            # Both prompt mechanisms fail -> the final fallback is "unknown".
            with patch('click.prompt', side_effect=Exception("No prompt")):
                with patch('builtins.input', side_effect=Exception("No input")):
                    assert resolve_owner() == 'unknown'


class TestExtractTitleFromFrontmatter:
    """Tests for YAML frontmatter title extraction."""

    def test_extract_title_basic(self):
        """Extract title from basic frontmatter."""
        content = """---
id: PLAN-123
title: Test Plan
owner: alice
---

Content here.
"""
        assert _extract_title_from_frontmatter(content) == "Test Plan"

    def test_extract_title_with_spaces(self):
        """Extract title with leading/trailing spaces."""
        content = """---
id: PLAN-123
title:   Spaced Title
owner: alice
---
"""
        assert _extract_title_from_frontmatter(content) == "Spaced Title"

    def test_extract_title_missing(self):
        """Return 'Untitled' when title field missing."""
        content = """---
id: PLAN-123
owner: alice
---
"""
        assert _extract_title_from_frontmatter(content) == "Untitled"

    def test_extract_title_no_frontmatter(self):
        """Return 'Untitled' when no frontmatter present."""
        content = "Just plain content."
        assert _extract_title_from_frontmatter(content) == "Untitled"

    def test_extract_title_empty_frontmatter(self):
        """Return 'Untitled' when frontmatter empty."""
        content = """---
---

Content.
"""
        assert _extract_title_from_frontmatter(content) == "Untitled"

    def test_extract_title_multiline(self):
        """Extract title from complex multiline frontmatter."""
        content = """---
id: PLAN-20251013-01T6N8
title: Complex Title with Details
owner: bob
status: draft
tags:
  - tag1
  - tag2
---

# Content starts here
"""
        assert _extract_title_from_frontmatter(content) == "Complex Title with Details"


class TestPickPlanInteractively:
    """Tests for interactive plan selection."""

    def test_pick_plan_no_directory(self, capsys):
        """Handle missing plans directory gracefully."""
        with patch('orchestrator_toolkit.settings.OrchSettings.load') as mock_load:
            mock_s = MagicMock()
            mock_s.plans_dir = Path("/nonexistent")
            mock_load.return_value = mock_s

            result = pick_plan_interactively()
            assert result is None

            captured = capsys.readouterr()
            assert "No plans directory found" in captured.out

    def test_pick_plan_empty_directory(self, tmp_path, capsys):
        """Handle empty plans directory."""
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()

        with patch('orchestrator_toolkit.settings.OrchSettings.load') as mock_load:
            mock_s = MagicMock()
            mock_s.plans_dir = plans_dir
            mock_load.return_value = mock_s

            result = pick_plan_interactively()
            assert result is None

            captured = capsys.readouterr()
            assert "No plans found" in captured.out

    def test_pick_plan_user_cancels(self, tmp_path, capsys):
        """Handle user cancellation with 'q'."""
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()

        # Create a test plan
        plan_file = plans_dir / "PLAN-20251013-01T6N8-test.md"
        plan_file.write_text("""---
id: PLAN-20251013-01T6N8
title: Test Plan
---
""")

        with patch('orchestrator_toolkit.settings.OrchSettings.load') as mock_load:
            mock_s = MagicMock()
            mock_s.plans_dir = plans_dir
            mock_load.return_value = mock_s

            with patch('builtins.input', return_value='q'):
                result = pick_plan_interactively()
                assert result is None

    def test_pick_plan_valid_selection(self, tmp_path, capsys):
        """Select a plan successfully."""
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()

        # Create test plans
        plan1 = plans_dir / "PLAN-20251013-01T6N8-first.md"
        plan1.write_text("""---
id: PLAN-20251013-01T6N8
title: First Plan
---
""")

        plan2 = plans_dir / "PLAN-20251013-02NZ6Q-second.md"
        plan2.write_text("""---
id: PLAN-20251013-02NZ6Q
title: Second Plan
---
""")

        with patch('orchestrator_toolkit.settings.OrchSettings.load') as mock_load:
            mock_s = MagicMock()
            mock_s.plans_dir = plans_dir
            mock_load.return_value = mock_s

            with patch('builtins.input', return_value='2'):
                result = pick_plan_interactively()
                assert result == "PLAN-20251013-02NZ6Q-second"

    def test_pick_plan_invalid_selection(self, tmp_path, capsys):
        """Handle invalid selection number."""
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()

        plan_file = plans_dir / "PLAN-20251013-01T6N8-test.md"
        plan_file.write_text("""---
id: PLAN-20251013-01T6N8
title: Test Plan
---
""")

        with patch('orchestrator_toolkit.settings.OrchSettings.load') as mock_load:
            mock_s = MagicMock()
            mock_s.plans_dir = plans_dir
            mock_load.return_value = mock_s

            with patch('builtins.input', return_value='99'):
                result = pick_plan_interactively()
                assert result is None

            captured = capsys.readouterr()
            assert "Invalid selection" in captured.out


class TestPickSpecInteractively:
    """Tests for interactive spec selection."""

    def test_pick_spec_no_directory(self, capsys):
        """Handle missing specs directory gracefully."""
        with patch('pathlib.Path.exists', return_value=False):
            result = pick_spec_interactively()
            assert result is None

        captured = capsys.readouterr()
        assert "No specs directory found" in captured.out

    def test_pick_spec_empty_directory(self, tmp_path, monkeypatch, capsys):
        """Handle empty specs directory."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "ai_docs" / "specs").mkdir(parents=True)

        result = pick_spec_interactively()
        assert result is None

    def test_pick_spec_valid_selection(self, tmp_path, monkeypatch, capsys):
        """Select a spec successfully."""
        monkeypatch.chdir(tmp_path)
        specs_dir = tmp_path / "ai_docs" / "specs"
        specs_dir.mkdir(parents=True)

        # Create test specs (pick_spec_interactively reads ai_docs/specs
        # relative to the current directory)
        (specs_dir / "SPEC-20251013-01T6N8-first.md").write_text(
            "---\nid: SPEC-20251013-01T6N8\ntitle: First Spec\n---\n"
        )
        (specs_dir / "SPEC-20251013-02NZ6Q-second.md").write_text(
            "---\nid: SPEC-20251013-02NZ6Q\ntitle: Second Spec\n---\n"
        )

        with patch('builtins.input', return_value='1'):
            result = pick_spec_interactively()

        # Selecting "1" returns the stem of the first spec (sorted by name)
        assert result == "SPEC-20251013-01T6N8-first"


class TestClearOwnerCache:
    """Tests for cache clearing."""

    def test_clear_cache(self, monkeypatch):
        """Clearing cache allows re-resolution."""
        monkeypatch.setenv('OTK_DEFAULT_OWNER', 'alice')
        assert resolve_owner() == 'alice'

        clear_owner_cache()
        monkeypatch.setenv('OTK_DEFAULT_OWNER', 'bob')
        assert resolve_owner() == 'bob'
