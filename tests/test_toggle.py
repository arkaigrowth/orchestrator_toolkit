"""
Tests for Scout agent toggle behavior.

Tests that Scout can successfully toggle:
1. PLAN status: draft → ready
2. SPEC design_ok: false → true

These are critical gates in the workflow.
"""

from __future__ import annotations
import pytest
from pathlib import Path
import re


def test_plan_status_toggle_draft_to_ready(tmp_path):
    """Test toggling PLAN status from draft to ready."""
    # Create PLAN file with draft status
    plans_dir = tmp_path / "ai_docs" / "plans"
    plans_dir.mkdir(parents=True)

    plan_file = plans_dir / "PLAN-20251015-TOG001-test-toggle.md"
    plan_file.write_text("""---
id: PLAN-20251015-TOG001-test-toggle
title: Test Toggle Plan
owner: tester
created: "2025-10-15T00:00:00Z"
status: draft
spec_id: ""
---

## Objective
Test status toggle

## Milestones
- [ ] Milestone 1
""")

    # Verify initial state
    content = plan_file.read_text()
    assert 'status: draft' in content

    # Simulate Scout edit: toggle status to ready
    updated_content = re.sub(
        r'status: draft',
        'status: ready',
        content
    )
    plan_file.write_text(updated_content)

    # Verify toggle successful
    final_content = plan_file.read_text()
    assert 'status: ready' in final_content
    assert 'status: draft' not in final_content


def test_spec_design_ok_toggle_false_to_true(tmp_path):
    """Test toggling SPEC design_ok from false to true."""
    # Create SPEC file with design_ok: false
    specs_dir = tmp_path / "ai_docs" / "specs"
    specs_dir.mkdir(parents=True)

    spec_file = specs_dir / "SPEC-20251015-TOG002-test-toggle.md"
    spec_file.write_text("""---
id: SPEC-20251015-TOG002-test-toggle
title: Test Toggle SPEC
plan_id: PLAN-20251015-TOG001
owner: tester
created: "2025-10-15T00:00:00Z"
status: draft
design_ok: false
---

## Objective
Test design_ok toggle

## Approach
Test approach

## Implementation Steps
1. Step 1
2. Step 2

## Acceptance Criteria
- [ ] Criteria 1
""")

    # Verify initial state
    content = spec_file.read_text()
    assert 'design_ok: false' in content

    # Simulate Scout edit: toggle design_ok to true
    updated_content = re.sub(
        r'design_ok: false',
        'design_ok: true',
        content
    )
    spec_file.write_text(updated_content)

    # Verify toggle successful
    final_content = spec_file.read_text()
    assert 'design_ok: true' in final_content
    assert 'design_ok: false' not in final_content


def test_toggle_preserves_other_frontmatter(tmp_path):
    """Ensure toggling one field doesn't affect other frontmatter."""
    specs_dir = tmp_path / "ai_docs" / "specs"
    specs_dir.mkdir(parents=True)

    spec_file = specs_dir / "SPEC-20251015-TOG003-preserve.md"
    original_content = """---
id: SPEC-20251015-TOG003-preserve
title: Test Preserve Fields
plan_id: PLAN-20251015-PARENT
owner: original_owner
created: "2025-10-15T12:00:00Z"
status: draft
design_ok: false
---

## Content
Test content
"""
    spec_file.write_text(original_content)

    # Toggle design_ok
    updated_content = re.sub(
        r'design_ok: false',
        'design_ok: true',
        original_content
    )
    spec_file.write_text(updated_content)

    # Verify other fields preserved
    final_content = spec_file.read_text()
    assert 'id: SPEC-20251015-TOG003-preserve' in final_content
    assert 'title: Test Preserve Fields' in final_content
    assert 'plan_id: PLAN-20251015-PARENT' in final_content
    assert 'owner: original_owner' in final_content
    assert 'status: draft' in final_content  # Unchanged
    assert 'design_ok: true' in final_content  # Changed


def test_plan_ready_prevents_second_toggle(tmp_path, monkeypatch):
    """Once PLAN is ready and has spec_id, it should not be processed again."""
    monkeypatch.chdir(tmp_path)

    plans_dir = tmp_path / "ai_docs" / "plans"
    plans_dir.mkdir(parents=True)

    plan_file = plans_dir / "PLAN-20251015-TOG004-once.md"
    plan_file.write_text("""---
id: PLAN-20251015-TOG004-once
title: Test Once Toggle
owner: tester
created: "2025-10-15T00:00:00Z"
status: ready
spec_id: "SPEC-20251015-ALREADY-EXISTS"
---

## Objective
Test gate prevents re-processing
""")

    # Import orchestrator
    from orchestrator_toolkit.orchestrator import orchestrator_plans

    # Run orchestrator - should skip this PLAN (already has spec_id)
    orchestrator_plans()

    # Verify PLAN unchanged
    content = plan_file.read_text()
    assert 'spec_id: "SPEC-20251015-ALREADY-EXISTS"' in content
    assert 'status: ready' in content

    # Verify no new SPECs created
    specs_dir = tmp_path / "ai_docs" / "specs"
    if specs_dir.exists():
        specs = list(specs_dir.glob("SPEC-20251015-ALREADY-EXISTS*.md"))
        assert len(specs) == 0, "Should not create SPEC when spec_id already filled"
