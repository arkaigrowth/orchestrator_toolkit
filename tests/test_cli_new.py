"""
Tests for Smart CLI Command (otk-new)
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import sys

from orchestrator_toolkit.cli_new import (
    create_plan_file,
    create_spec_file,
    create_exec_log,
    handle_plan_command,
    handle_spec_command,
    handle_execute_command,
    main
)
from orchestrator_toolkit.owner import clear_owner_cache


@pytest.fixture(autouse=True)
def reset_cache():
    """Clear owner cache before each test."""
    clear_owner_cache()
    yield
    clear_owner_cache()


@pytest.fixture
def mock_settings(tmp_path):
    """Mock OrchSettings with temp directories."""
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()

    mock_s = MagicMock()
    mock_s.plans_dir = plans_dir

    with patch('orchestrator_toolkit.cli_new.OrchSettings') as mock_cls:
        mock_cls.load.return_value = mock_s
        yield mock_s


class TestCreatePlanFile:
    """Tests for PLAN file creation."""

    def test_create_plan_basic(self, mock_settings):
        """Create a basic plan file."""
        result = create_plan_file("Test Plan", "alice")

        assert result.exists()
        assert result.parent == mock_settings.plans_dir
        assert result.name.startswith("PLAN-")
        assert result.suffix == ".md"

        content = result.read_text()
        assert "title: Test Plan" in content
        assert "owner: alice" in content
        assert "status: draft" in content

    def test_create_plan_auto_template(self, mock_settings, tmp_path):
        """Auto-create template if missing."""
        # Ensure template doesn't exist
        template_path = Path(".claude/templates/plan.md")
        if template_path.exists():
            template_path.unlink()

        result = create_plan_file("Auto Template Test", "bob")

        assert result.exists()
        # Template should be auto-created
        assert template_path.exists()

    def test_create_plan_id_format(self, mock_settings):
        """Verify PLAN ID format."""
        result = create_plan_file("Format Test", "charlie")

        # ID should match PLAN-YYYYMMDD-ULID6-slug format
        import re
        pattern = r'PLAN-\d{8}-[A-Z0-9]{6}-.+\.md'
        assert re.match(pattern, result.name)

        content = result.read_text()
        # ID in content should match filename (minus .md)
        assert f"id: {result.stem}" in content


class TestCreateSpecFile:
    """Tests for SPEC file creation."""

    def test_create_spec_basic(self, tmp_path):
        """Create a basic spec file."""
        # Change to tmp directory for spec creation
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = create_spec_file("Test Spec", "alice")

            assert result.exists()
            assert result.parent.name == "specs"
            assert result.name.startswith("SPEC-")
            assert result.suffix == ".md"

            content = result.read_text()
            assert "title: Test Spec" in content
            assert "owner: alice" in content
            assert "status: draft" in content
        finally:
            os.chdir(original_cwd)

    def test_create_spec_with_plan_ref(self, tmp_path):
        """Create spec with parent plan reference."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = create_spec_file(
                "Linked Spec",
                "bob",
                plan_id_ref="PLAN-20251013-01T6N8-parent"
            )

            content = result.read_text()
            assert "plan: PLAN-20251013-01T6N8-parent" in content
        finally:
            os.chdir(original_cwd)

    def test_create_spec_auto_directory(self, tmp_path):
        """Auto-create specs directory if missing."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            specs_dir = tmp_path / "ai_docs" / "specs"
            assert not specs_dir.exists()

            result = create_spec_file("Auto Dir Test", "charlie")

            assert specs_dir.exists()
            assert result.exists()
        finally:
            os.chdir(original_cwd)


class TestCreateExecLog:
    """Tests for execution log creation."""

    def test_create_exec_log_basic(self, tmp_path):
        """Create a basic execution log."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = create_exec_log("SPEC-20251013-01T6N8-test", "alice")

            assert result.exists()
            assert result.parent.name == "exec_logs"
            assert "exec" in result.name
            assert result.suffix == ".md"

            content = result.read_text()
            assert "spec: SPEC-20251013-01T6N8-test" in content
            assert "owner: alice" in content
            assert "status: running" in content
        finally:
            os.chdir(original_cwd)

    def test_create_exec_log_filename_format(self, tmp_path):
        """Verify execution log filename format."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            spec_id = "SPEC-20251013-01T6N8-auth"
            result = create_exec_log(spec_id, "bob")

            # Filename should be: SPEC-...-exec-TIMESTAMP.md
            assert result.name.startswith(spec_id)
            assert "-exec-" in result.name
            assert result.name.endswith(".md")
        finally:
            os.chdir(original_cwd)


class TestHandlePlanCommand:
    """Tests for plan command handler."""

    def test_handle_plan_with_title(self, mock_settings, capsys):
        """Handle plan creation with provided title."""
        exit_code = handle_plan_command("New Plan", "alice")

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "✅ Created:" in captured.out
        assert "PLAN-" in captured.out

    def test_handle_plan_prompt_title(self, mock_settings, capsys):
        """Prompt for title when not provided."""
        with patch('builtins.input', return_value='Prompted Plan'):
            exit_code = handle_plan_command("", "bob")

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "✅ Created:" in captured.out

    def test_handle_plan_cancel_prompt(self, mock_settings, capsys):
        """Handle user cancellation during title prompt."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            exit_code = handle_plan_command("", "charlie")

            assert exit_code == 1
            captured = capsys.readouterr()
            assert "❌ Cancelled" in captured.out

    def test_handle_plan_error(self, mock_settings, capsys):
        """Handle errors during plan creation."""
        with patch('orchestrator_toolkit.cli_new.create_plan_file', side_effect=Exception("Test error")):
            exit_code = handle_plan_command("Error Plan", "dave")

            assert exit_code == 1
            captured = capsys.readouterr()
            # Error goes to stderr, not stdout
            assert "❌ Error creating plan" in captured.err


class TestHandleSpecCommand:
    """Tests for spec command handler."""

    @patch('orchestrator_toolkit.cli_new.pick_plan_interactively')
    def test_handle_spec_with_plan(self, mock_pick, tmp_path, capsys):
        """Handle spec creation with plan reference."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            mock_pick.return_value = "PLAN-20251013-01T6N8-test"

            exit_code = handle_spec_command(
                "Test Spec",
                "alice",
                plan_id_ref="PLAN-20251013-01T6N8-test"
            )

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "✅ Created:" in captured.out
            assert "SPEC-" in captured.out
            assert "Parent: PLAN-" in captured.out
        finally:
            os.chdir(original_cwd)

    @patch('orchestrator_toolkit.cli_new.pick_plan_interactively')
    def test_handle_spec_prompt_plan(self, mock_pick, tmp_path, capsys):
        """Prompt for plan when not provided."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            mock_pick.return_value = "PLAN-20251013-02NZ6Q-selected"

            exit_code = handle_spec_command("Spec with Selected Plan", "bob")

            assert exit_code == 0
            mock_pick.assert_called_once()
        finally:
            os.chdir(original_cwd)

    @patch('orchestrator_toolkit.cli_new.pick_plan_interactively')
    def test_handle_spec_no_plan_selected(self, mock_pick, tmp_path, capsys):
        """Handle no plan selected (create spec anyway)."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            mock_pick.return_value = None

            exit_code = handle_spec_command("Orphan Spec", "charlie")

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "No plan selected" in captured.out
        finally:
            os.chdir(original_cwd)

    @patch('orchestrator_toolkit.cli_new.pick_plan_interactively')
    def test_handle_spec_prompt_title(self, mock_pick, tmp_path):
        """Prompt for title when not provided."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            mock_pick.return_value = None

            with patch('builtins.input', return_value='Prompted Spec'):
                exit_code = handle_spec_command("", "dave")

                assert exit_code == 0
        finally:
            os.chdir(original_cwd)


class TestHandleExecuteCommand:
    """Tests for execute command handler."""

    @patch('orchestrator_toolkit.cli_new.pick_spec_interactively')
    def test_handle_execute_with_spec(self, mock_pick, tmp_path, capsys):
        """Handle execution with spec reference."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            exit_code = handle_execute_command(
                "alice",
                spec_id_ref="SPEC-20251013-01T6N8-test"
            )

            assert exit_code == 0
            captured = capsys.readouterr()
            assert "✅ Execution log created:" in captured.out
            assert "Spec: SPEC-" in captured.out
        finally:
            os.chdir(original_cwd)

    @patch('orchestrator_toolkit.cli_new.pick_spec_interactively')
    def test_handle_execute_prompt_spec(self, mock_pick, tmp_path, capsys):
        """Prompt for spec when not provided."""
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            mock_pick.return_value = "SPEC-20251013-02NZ6Q-selected"

            exit_code = handle_execute_command("bob")

            assert exit_code == 0
            mock_pick.assert_called_once()
        finally:
            os.chdir(original_cwd)

    @patch('orchestrator_toolkit.cli_new.pick_spec_interactively')
    def test_handle_execute_no_spec_selected(self, mock_pick, capsys):
        """Handle no spec selected (abort)."""
        mock_pick.return_value = None

        exit_code = handle_execute_command("charlie")

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "❌ No spec selected" in captured.out


class TestMain:
    """Tests for main CLI entry point."""

    @patch('orchestrator_toolkit.cli_new.resolve_owner')
    @patch('orchestrator_toolkit.cli_new.handle_plan_command')
    def test_main_plan_command(self, mock_handle, mock_owner, monkeypatch):
        """Route plan command through main."""
        mock_owner.return_value = "alice"
        mock_handle.return_value = 0

        # Use "create" instead of "implement" to route to PLAN
        monkeypatch.setattr(sys, 'argv', ['otk-new', 'create auth system'])

        exit_code = main()

        assert exit_code == 0
        mock_handle.assert_called_once()

    @patch('orchestrator_toolkit.cli_new.resolve_owner')
    @patch('orchestrator_toolkit.cli_new.handle_spec_command')
    def test_main_spec_command(self, mock_handle, mock_owner, monkeypatch):
        """Route spec command through main."""
        mock_owner.return_value = "bob"
        mock_handle.return_value = 0

        monkeypatch.setattr(sys, 'argv', ['otk-new', 'spec for plan-123'])

        exit_code = main()

        assert exit_code == 0
        mock_handle.assert_called_once()

    @patch('orchestrator_toolkit.cli_new.resolve_owner')
    @patch('orchestrator_toolkit.cli_new.handle_execute_command')
    def test_main_execute_command(self, mock_handle, mock_owner, monkeypatch):
        """Route execute command through main."""
        mock_owner.return_value = "charlie"
        mock_handle.return_value = 0

        monkeypatch.setattr(sys, 'argv', ['otk-new', 'execute spec-456'])

        exit_code = main()

        assert exit_code == 0
        mock_handle.assert_called_once()

    def test_main_no_args(self, capsys, monkeypatch):
        """Handle no arguments provided."""
        monkeypatch.setattr(sys, 'argv', ['otk-new'])

        exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    @patch('orchestrator_toolkit.cli_new.extract_owner_from_text')
    @patch('orchestrator_toolkit.cli_new.resolve_owner')
    @patch('orchestrator_toolkit.cli_new.handle_plan_command')
    def test_main_explicit_owner(self, mock_handle, mock_resolve, mock_extract, monkeypatch):
        """Use explicit owner from command text."""
        mock_extract.return_value = ("explicit-owner", "create plan")
        mock_handle.return_value = 0

        monkeypatch.setattr(sys, 'argv', ['otk-new', 'create plan --owner explicit-owner'])

        exit_code = main()

        assert exit_code == 0
        # resolve_owner should not be called when explicit owner provided
        mock_resolve.assert_not_called()
        # Should call handle with explicit owner
        assert mock_handle.call_args[0][1] == "explicit-owner"

    def test_main_multi_word_input(self, monkeypatch, capsys):
        """Handle multi-word user input."""
        with patch('orchestrator_toolkit.cli_new.resolve_owner', return_value='test'):
            with patch('orchestrator_toolkit.cli_new.handle_plan_command', return_value=0):
                # Use "new" instead of "implement" to route to PLAN
                monkeypatch.setattr(sys, 'argv', [
                    'otk-new',
                    'new',
                    'authentication',
                    'system',
                    'with',
                    'JWT'
                ])

                exit_code = main()
                assert exit_code == 0
