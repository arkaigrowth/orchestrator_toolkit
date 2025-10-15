"""
Tests for PLAN/SPEC workflow gates.

Tests orchestrator gates that prevent premature execution:
1. Orchestrator only processes PLANs with status: ready
2. SPECs created with design_ok: false by default
3. Idempotent SPEC creation (no duplicates)
"""

from __future__ import annotations
import pytest
from pathlib import Path
from orchestrator_toolkit.orchestrator import orchestrator_plans


def test_orchestrator_refuses_non_ready_plans(tmp_path, monkeypatch):
    """Orchestrator should skip PLANs without status: ready."""
    monkeypatch.chdir(tmp_path)

    # Create test directory structure
    plans_dir = tmp_path / "ai_docs" / "plans"
    plans_dir.mkdir(parents=True)

    # Create draft PLAN (not ready)
    draft_plan = plans_dir / "PLAN-20251015-DRAFT1-test-plan.md"
    draft_plan.write_text("""---
id: PLAN-20251015-DRAFT1-test-plan
title: Test Draft Plan
owner: tester
created: "2025-10-15T00:00:00Z"
status: draft
spec_id: ""
---

## Objective
Test objective

## Milestones
- [ ] Milestone 1
""")

    # Run orchestrator
    result = orchestrator_plans()

    # Verify no SPECs created for draft PLANs
    specs_dir = tmp_path / "ai_docs" / "specs"
    if specs_dir.exists():
        specs = list(specs_dir.glob("SPEC-*.md"))
        assert len(specs) == 0, "Orchestrator should not create SPECs for draft PLANs"

    # Verify PLAN unchanged
    plan_content = draft_plan.read_text()
    assert 'status: draft' in plan_content
    assert 'spec_id: ""' in plan_content


def test_spec_template_includes_design_ok_false(tmp_path, monkeypatch):
    """SPECs created by orchestrator should have design_ok: false."""
    monkeypatch.chdir(tmp_path)

    # Create test directory structure
    plans_dir = tmp_path / "ai_docs" / "plans"
    plans_dir.mkdir(parents=True)

    # Create ready PLAN
    ready_plan = plans_dir / "PLAN-20251015-READY1-test-plan.md"
    ready_plan.write_text("""---
id: PLAN-20251015-READY1-test-plan
title: Test Ready Plan
owner: tester
created: "2025-10-15T00:00:00Z"
status: ready
spec_id: ""
---

## Objective
Test objective for ready plan

## Milestones
- [ ] Milestone 1
""")

    # Run orchestrator
    result = orchestrator_plans()

    # Verify SPEC created with design_ok: false
    specs_dir = tmp_path / "ai_docs" / "specs"
    assert specs_dir.exists(), "Specs directory should be created"

    specs = list(specs_dir.glob("SPEC-*.md"))
    assert len(specs) == 1, f"Expected 1 SPEC, found {len(specs)}"

    spec_content = specs[0].read_text()
    assert 'design_ok: false' in spec_content, "SPEC should have design_ok: false"
    # Check for plan reference (either plan: or plan_id: format)
    assert ('plan_id: PLAN-20251015-READY1-test-plan' in spec_content or
            'plan: PLAN-20251015-READY1-test-plan' in spec_content), "SPEC should reference parent PLAN"


def test_idempotent_spec_creation(tmp_path, monkeypatch):
    """Running orchestrator twice should not create duplicate SPECs."""
    monkeypatch.chdir(tmp_path)

    # Create test directory structure
    plans_dir = tmp_path / "ai_docs" / "plans"
    plans_dir.mkdir(parents=True)

    # Create ready PLAN
    ready_plan = plans_dir / "PLAN-20251015-IDEM01-test-plan.md"
    ready_plan.write_text("""---
id: PLAN-20251015-IDEM01-test-plan
title: Test Idempotent Plan
owner: tester
created: "2025-10-15T00:00:00Z"
status: ready
spec_id: ""
---

## Objective
Test idempotency

## Milestones
- [ ] Milestone 1
""")

    # Run orchestrator first time
    orchestrator_plans()

    # Count SPECs created
    specs_dir = tmp_path / "ai_docs" / "specs"
    specs_first = list(specs_dir.glob("SPEC-*.md"))
    assert len(specs_first) == 1, f"Expected 1 SPEC after first run, found {len(specs_first)}"

    # Verify PLAN was updated with spec_id
    plan_content = ready_plan.read_text()
    assert 'spec_id: ""' not in plan_content, "PLAN should have spec_id filled"
    assert 'SPEC-' in plan_content, "PLAN should reference created SPEC"

    # Run orchestrator second time
    orchestrator_plans()

    # Count SPECs again - should be same
    specs_second = list(specs_dir.glob("SPEC-*.md"))
    assert len(specs_second) == 1, f"Expected 1 SPEC after second run (idempotent), found {len(specs_second)}"


def test_orchestrator_gate_both_conditions(tmp_path, monkeypatch):
    """Orchestrator requires BOTH status: ready AND spec_id: empty."""
    monkeypatch.chdir(tmp_path)

    plans_dir = tmp_path / "ai_docs" / "plans"
    plans_dir.mkdir(parents=True)

    # Create PLAN with spec_id already filled (should be skipped)
    existing_spec_plan = plans_dir / "PLAN-20251015-EXIST1-test-plan.md"
    existing_spec_plan.write_text("""---
id: PLAN-20251015-EXIST1-test-plan
title: Plan With Existing SPEC
owner: tester
created: "2025-10-15T00:00:00Z"
status: ready
spec_id: "SPEC-20251015-OLDSPEC"
---

## Objective
Test gate logic

## Milestones
- [ ] Milestone 1
""")

    # Run orchestrator
    orchestrator_plans()

    # Verify no new SPECs created (PLAN already has spec_id)
    specs_dir = tmp_path / "ai_docs" / "specs"
    if specs_dir.exists():
        specs = list(specs_dir.glob("SPEC-*.md"))
        # Should be 0 new SPECs (or only old ones if any existed before)
        assert len(specs) == 0, "Orchestrator should not create SPEC when spec_id already filled"
