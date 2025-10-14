"""
Integration tests for orchestrator PLAN → SPEC workflow.

Tests the actual orchestrator_plans() function to ensure idempotency
and correct state transitions.
"""
import tempfile
import shutil
from pathlib import Path
import pytest

from orchestrator_toolkit.orchestrator import orchestrator_plans
from orchestrator_toolkit.settings import OrchSettings
from orchestrator_toolkit.cli_new import create_plan_file, mark_plan_ready


class TestOrchestratorIntegration:
    """Integration tests for orchestrator workflow."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="otk_test_")
        original_cwd = Path.cwd()

        # Create required directories
        workspace = Path(temp_dir)
        (workspace / "ai_docs" / "plans").mkdir(parents=True)
        (workspace / "ai_docs" / "specs").mkdir(parents=True)
        (workspace / "ai_docs" / "exec_logs").mkdir(parents=True)
        (workspace / ".claude" / "templates").mkdir(parents=True)

        # Copy template file
        template_src = original_cwd / ".claude" / "templates" / "plan.md"
        if template_src.exists():
            shutil.copy(template_src, workspace / ".claude" / "templates" / "plan.md")

        # Change to temp directory
        import os
        os.chdir(workspace)

        yield workspace

        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_orchestrator_creates_spec_from_ready_plan(self, temp_workspace):
        """Test that orchestrator creates SPEC from ready PLAN."""
        # Create a PLAN with status=ready
        plan_path = create_plan_file("Test Authentication", "testuser", status="ready")
        assert plan_path.exists()

        # Run orchestrator
        created = orchestrator_plans()
        assert created == 1, "Should create exactly 1 SPEC"

        # Verify SPEC was created
        specs_dir = temp_workspace / "ai_docs" / "specs"
        spec_files = list(specs_dir.glob("SPEC-*.md"))
        assert len(spec_files) == 1, "Should have exactly 1 SPEC file"

        # Verify PLAN was updated
        plan_content = plan_path.read_text()
        assert "status: in-spec" in plan_content
        assert "spec_id: \"SPEC-" in plan_content

    def test_orchestrator_idempotency(self, temp_workspace):
        """Test that orchestrator is idempotent - won't create duplicate SPECs."""
        # Create a PLAN with status=ready
        plan_path = create_plan_file("Test Feature", "testuser", status="ready")

        # Run orchestrator first time
        created1 = orchestrator_plans()
        assert created1 == 1, "First run should create 1 SPEC"

        # Run orchestrator second time
        created2 = orchestrator_plans()
        assert created2 == 0, "Second run should create 0 SPECs (idempotent)"

        # Verify still only 1 SPEC exists
        specs_dir = temp_workspace / "ai_docs" / "specs"
        spec_files = list(specs_dir.glob("SPEC-*.md"))
        assert len(spec_files) == 1, "Should still have exactly 1 SPEC file"

    def test_orchestrator_handles_multiple_ready_plans(self, temp_workspace):
        """Test orchestrator handles multiple ready PLANs."""
        # Create 3 PLANs with status=ready
        plan1 = create_plan_file("Feature 1", "user1", status="ready")
        plan2 = create_plan_file("Feature 2", "user2", status="ready")
        plan3 = create_plan_file("Feature 3", "user3", status="ready")

        # Run orchestrator
        created = orchestrator_plans()
        assert created == 3, "Should create 3 SPECs for 3 ready PLANs"

        # Verify all PLANs updated
        for plan_path in [plan1, plan2, plan3]:
            content = plan_path.read_text()
            assert "status: in-spec" in content
            assert "spec_id: \"SPEC-" in content

    def test_orchestrator_ignores_draft_plans(self, temp_workspace):
        """Test orchestrator ignores PLANs that aren't ready."""
        # Create PLANs with various non-ready statuses
        draft_plan = create_plan_file("Draft Feature", "user", status="draft")
        done_plan = create_plan_file("Done Feature", "user", status="done")
        ready_plan = create_plan_file("Ready Feature", "user", status="ready")

        # Manually set done plan status (since create_plan_file doesn't support it)
        done_content = done_plan.read_text()
        done_content = done_content.replace("status: done", "status: done")
        done_plan.write_text(done_content)

        # Run orchestrator
        created = orchestrator_plans()
        assert created == 1, "Should only create SPEC for ready PLAN"

        # Verify only ready plan was processed
        ready_content = ready_plan.read_text()
        assert "status: in-spec" in ready_content

        draft_content = draft_plan.read_text()
        assert "status: draft" in draft_content  # Unchanged

    def test_orchestrator_logs_to_exec_logs(self, temp_workspace):
        """Test that orchestrator logs actions to exec_logs."""
        # Create a ready PLAN
        plan_path = create_plan_file("Test Logging", "testuser", status="ready")

        # Run orchestrator
        created = orchestrator_plans()
        assert created == 1

        # Check for log file
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        log_file = temp_workspace / "ai_docs" / "exec_logs" / f"orchestrate-{today}.md"

        assert log_file.exists(), "Orchestration log should exist"
        log_content = log_file.read_text()
        assert "Created SPEC-" in log_content
        assert "from PLAN-" in log_content

    def test_mark_plan_ready_workflow(self, temp_workspace):
        """Test marking a draft PLAN as ready and then orchestrating."""
        # Create draft PLAN
        plan_path = create_plan_file("Draft to Ready", "testuser", status="draft")
        plan_id = plan_path.stem

        # Mark as ready
        result = mark_plan_ready(plan_id)
        assert result == 0, "Should successfully mark as ready"

        # Verify status changed
        content = plan_path.read_text()
        assert "status: ready" in content

        # Run orchestrator
        created = orchestrator_plans()
        assert created == 1, "Should create SPEC for newly ready PLAN"

        # Verify SPEC created and PLAN updated
        content = plan_path.read_text()
        assert "status: in-spec" in content
        assert "spec_id: \"SPEC-" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])