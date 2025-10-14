"""
Smart CLI Command (otk-new)

Natural language interface for PLAN/SPEC/EXECUTE workflow.
Uses phrase_router to interpret user input and route to appropriate command.
"""
import sys
from pathlib import Path
from typing import Optional

from .phrase_router import route_intent, extract_owner_from_text
from .owner import resolve_owner, pick_plan_interactively, pick_spec_interactively
from .ids import plan_id, spec_id, slugify
from .settings import OrchSettings
from .utils import now_iso


def create_plan_file(title: str, owner: str, status: str = "draft") -> Path:
    """
    Create a new PLAN file with ULID-based ID.

    Args:
        title: Plan title
        owner: Owner name
        status: Initial status (draft or ready)

    Returns:
        Path to created plan file
    """
    s = OrchSettings.load()
    pid = plan_id(title)

    template = Path(".claude/templates/plan.md")
    if not template.exists():
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_text(
            "---\n"
            "id: ${ID}\n"
            "title: ${TITLE}\n"
            "owner: ${OWNER}\n"
            "created: ${DATE}\n"
            "status: ${STATUS}\n"
            "spec_id: \"\"\n"
            "---\n\n"
            "## Overview\n\n(Scaffolded by orchestrator.)\n\n"
            "## Steps\n\n1. Draft approach\n2. Identify inputs\n3. Produce deliverable\n\n"
            "## References\n\n- (add paths / URLs)\n",
            encoding="utf-8"
        )

    content = template.read_text()
    content = content.replace("${ID}", pid)
    content = content.replace("${TITLE}", title)
    content = content.replace("${OWNER}", owner)
    content = content.replace("${DATE}", now_iso())
    content = content.replace("${STATUS}", status)

    # Use the ID as filename
    out = s.plans_dir / f"{pid}.md"
    out.write_text(content, encoding="utf-8")
    return out


def create_spec_file(title: str, owner: str, plan_id_ref: Optional[str] = None) -> Path:
    """
    Create a new SPEC file with ULID-based ID.

    Args:
        title: Spec title
        owner: Owner name
        plan_id_ref: Optional parent PLAN ID reference

    Returns:
        Path to created spec file
    """
    specs_dir = Path("ai_docs/specs")
    specs_dir.mkdir(parents=True, exist_ok=True)

    sid = spec_id(title)

    template_content = (
        "---\n"
        "id: ${ID}\n"
        "title: ${TITLE}\n"
        "owner: ${OWNER}\n"
        "plan: ${PLAN_ID}\n"
        "created: ${DATE}\n"
        "status: draft\n"
        "---\n\n"
        "## Objective\n\n${TITLE}\n\n"
        "## Approach\n\n- [ ] Step 1\n- [ ] Step 2\n- [ ] Step 3\n\n"
        "## Acceptance Criteria\n\n- [ ] Criterion 1\n- [ ] Criterion 2\n\n"
    )

    content = template_content.replace("${ID}", sid)
    content = content.replace("${TITLE}", title)
    content = content.replace("${OWNER}", owner)
    content = content.replace("${PLAN_ID}", plan_id_ref or "")
    content = content.replace("${DATE}", now_iso())

    out = specs_dir / f"{sid}.md"
    out.write_text(content, encoding="utf-8")
    return out


def create_exec_log(spec_id_ref: str, owner: str) -> Path:
    """
    Create a new execution log file for a spec.

    Args:
        spec_id_ref: SPEC ID being executed
        owner: Owner name

    Returns:
        Path to created exec log file
    """
    logs_dir = Path("ai_docs/exec_logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Generate log filename from spec ID and timestamp
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    log_name = f"{spec_id_ref}-exec-{timestamp}.md"

    template_content = (
        "---\n"
        "spec: ${SPEC_ID}\n"
        "owner: ${OWNER}\n"
        "started: ${DATE}\n"
        "status: running\n"
        "---\n\n"
        "## Execution Log\n\n"
        "Executing spec: ${SPEC_ID}\n\n"
        "### Progress\n\n"
        "- [ ] Step 1\n"
        "- [ ] Step 2\n\n"
        "### Notes\n\n"
        "(Add execution notes here)\n\n"
    )

    content = template_content.replace("${SPEC_ID}", spec_id_ref)
    content = content.replace("${OWNER}", owner)
    content = content.replace("${DATE}", now_iso())

    out = logs_dir / log_name
    out.write_text(content, encoding="utf-8")
    return out


def mark_plan_ready(plan_id: str) -> int:
    """
    Mark an existing PLAN as ready for orchestration.

    Args:
        plan_id: PLAN ID to mark as ready

    Returns:
        Exit code (0 = success)
    """
    from pathlib import Path
    import re

    s = OrchSettings.load()

    # Find the plan file
    plan_files = list(s.plans_dir.glob(f"{plan_id}*.md"))
    if not plan_files:
        print(f"❌ PLAN not found: {plan_id}")
        return 1

    plan_file = plan_files[0]
    content = plan_file.read_text(encoding="utf-8")

    # Update status to ready
    updated_content = re.sub(
        r'status:\s*[^\n]+',
        'status: ready',
        content,
        count=1
    )

    if updated_content == content:
        print(f"⚠️  PLAN already marked as ready: {plan_id}")
        return 0

    plan_file.write_text(updated_content, encoding="utf-8")
    print(f"✅ Marked as ready: {plan_id}")
    print(f"   Run 'otk orchestrate' to create SPEC")
    return 0


def handle_plan_command(title: str, owner: str, ready: bool = False) -> int:
    """
    Handle PLAN creation.

    Args:
        title: Plan title
        owner: Owner name
        ready: If True, create with status=ready

    Returns:
        Exit code (0 = success)
    """
    if not title or title == "Untitled":
        try:
            title = input("Plan title: ").strip() or "Untitled"
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled")
            return 1

    try:
        status = "ready" if ready else "draft"
        out = create_plan_file(title, owner, status)
        print(f"✅ Created: {out}")
        print(f"   ID: {out.stem}")
        print(f"   Status: {status}")
        if ready:
            print(f"   Run 'otk orchestrate' to create SPEC")
        return 0
    except Exception as e:
        print(f"❌ Error creating plan: {e}", file=sys.stderr)
        return 1


def handle_spec_command(title: str, owner: str, plan_id_ref: Optional[str] = None) -> int:
    """
    Handle SPEC creation.

    Args:
        title: Spec title
        owner: Owner name
        plan_id_ref: Optional parent PLAN ID

    Returns:
        Exit code (0 = success)
    """
    # Prompt for plan if not provided
    if not plan_id_ref:
        print("\n📋 Select a parent plan for this spec:")
        plan_id_ref = pick_plan_interactively()
        if not plan_id_ref:
            print("❌ No plan selected. Creating spec without parent plan.")

    # Prompt for title if missing
    if not title or title == "Specification":
        try:
            title = input("Spec title: ").strip() or "Specification"
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled")
            return 1

    try:
        out = create_spec_file(title, owner, plan_id_ref)
        print(f"✅ Created: {out}")
        print(f"   ID: {out.stem}")
        if plan_id_ref:
            print(f"   Parent: {plan_id_ref}")
        return 0
    except Exception as e:
        print(f"❌ Error creating spec: {e}", file=sys.stderr)
        return 1


def handle_execute_command(owner: str, spec_id_ref: Optional[str] = None) -> int:
    """
    Handle EXECUTE command.

    Args:
        owner: Owner name
        spec_id_ref: Optional SPEC ID to execute

    Returns:
        Exit code (0 = success)
    """
    # Prompt for spec if not provided
    if not spec_id_ref:
        print("\n📐 Select a spec to execute:")
        spec_id_ref = pick_spec_interactively()
        if not spec_id_ref:
            print("❌ No spec selected.")
            return 1

    try:
        out = create_exec_log(spec_id_ref, owner)
        print(f"✅ Execution log created: {out}")
        print(f"   Spec: {spec_id_ref}")
        print(f"\n💡 Next: Edit {out} to track execution progress")
        return 0
    except Exception as e:
        print(f"❌ Error creating execution log: {e}", file=sys.stderr)
        return 1


def main():
    """
    Main CLI entry point for otk-new command.

    Usage:
        otk-new "implement auth system"
        otk-new "spec for plan-123"
        otk-new "execute spec-456"
        otk-new "design login flow"
    """
    # Get user input from command line arguments
    args = sys.argv[1:]
    if not args:
        print("Usage: otk-new <natural-language-command>")
        print("\nExamples:")
        print('  otk-new "implement auth system"')
        print('  otk-new "spec for plan-123"')
        print('  otk-new "execute spec-456"')
        print('  otk-new "design login flow"')
        return 1

    user_input = " ".join(args)

    # Extract owner from text if present
    explicit_owner, cleaned_input = extract_owner_from_text(user_input)

    # Route intent through phrase router
    command, target_id, title = route_intent(cleaned_input)

    # Resolve owner
    owner = explicit_owner or resolve_owner()

    print(f"\n🎯 Command: {command.upper()}")
    if target_id:
        print(f"   Target: {target_id}")
    if title:
        print(f"   Title: {title}")
    print(f"   Owner: {owner}")
    print()

    # Route to appropriate handler
    if command == "plan":
        # Check if "--ready" flag is in the original input
        ready = "--ready" in user_input
        return handle_plan_command(title, owner, ready)
    elif command == "spec":
        return handle_spec_command(title, owner, target_id)
    elif command == "execute":
        return handle_execute_command(owner, target_id)
    elif command == "ready" and target_id:
        # Handle marking plan as ready: "otk-new ready PLAN-xxx"
        return mark_plan_ready(target_id)
    else:
        print(f"❌ Unknown command: {command}", file=sys.stderr)
        return 1


def plan_new_direct():
    """Direct entry point for otk-plan-new command."""
    args = sys.argv[1:]
    if not args:
        print("Usage: otk-plan-new <title>")
        return 1
    title = " ".join(args)
    owner = resolve_owner()
    return handle_plan_command(title, owner)


def spec_new_direct():
    """Direct entry point for otk-spec-new command."""
    args = sys.argv[1:]
    if not args:
        # If no args, use the natural language interface
        return main()

    # Check if it looks like natural language vs structured command
    if len(args) == 1 or not args[0].startswith(('P-', 'PLAN-')):
        # Treat as natural language
        sys.argv = ['otk-new'] + args
        return main()

    # Structured command: otk-spec-new PLAN-ID "title"
    plan_id_ref = args[0]
    title = " ".join(args[1:]) if len(args) > 1 else "Specification"
    owner = resolve_owner()
    return handle_spec_command(title, owner, plan_id_ref)


def exec_direct():
    """Direct entry point for otk-exec command."""
    args = sys.argv[1:]
    if not args:
        # If no args, prompt interactively
        owner = resolve_owner()
        return handle_execute_command(owner, None)

    # Check if it looks like a spec ID
    if args[0].startswith(('S-', 'SPEC-')):
        spec_id_ref = args[0]
        owner = resolve_owner()
        return handle_execute_command(owner, spec_id_ref)
    else:
        # Treat as natural language
        sys.argv = ['otk-new', 'execute'] + args
        return main()


if __name__ == "__main__":
    raise SystemExit(main())
