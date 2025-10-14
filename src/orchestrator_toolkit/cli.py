from __future__ import annotations
import argparse, sys, subprocess

def _run(cmd: str) -> str:
    p = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    return p.stdout.strip()

def task_new():
    """
    Delegate to Python-based task creation (deprecated).

    Tasks are deprecated in favor of PLAN/SPEC/EXECUTE model.
    Use 'otk-new' or 'otk-plan-new' for new workflow.
    """
    from .scripts.task_new import main
    main()

def plan_new():
    """
    Delegate to ULID-based plan creation (back-compat shim).

    Legacy command that now creates ULID-based plans.
    For new workflow, use 'otk-new' or 'otk-plan-new'.
    """
    from .scripts.plan_new import main
    main()

def plan_summarize():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_id")
    ns = ap.parse_args()
    out = _run(f'.claude/commands/summarize-plan.sh "{ns.plan_id}"')
    print(out)

def orchestrator_once():
    from .orchestrator import once
    c = once()
    print(f"created_plans={c}")

def orchestrate():
    """Run PLAN → SPEC orchestration."""
    from .orchestrator import orchestrator_plans
    created = orchestrator_plans()
    if created > 0:
        print(f"✅ Created {created} SPEC(s)")
    else:
        print("📋 No PLANs ready for orchestration")
    return 0

def owner_who():
    """Show current owner resolution."""
    from .owner import resolve_owner
    import os
    from pathlib import Path

    owner = resolve_owner()
    print(f"Current owner: {owner}")
    print("\nResolution chain:")

    # Check environment variable
    if os.getenv("OTK_OWNER"):
        print(f"  1. ✅ Environment: OTK_OWNER={os.getenv('OTK_OWNER')}")
    else:
        print("  1. ❌ Environment: OTK_OWNER not set")

    # Check .otk/.owner file
    owner_file = Path(".otk/.owner")
    if owner_file.exists():
        stored_owner = owner_file.read_text().strip()
        print(f"  2. ✅ File: .otk/.owner = {stored_owner}")
    else:
        print("  2. ❌ File: .otk/.owner not found")

    # Show git config
    try:
        import subprocess
        git_user = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True, check=False
        ).stdout.strip()
        if git_user:
            print(f"  3. ✅ Git: user.name = {git_user}")
        else:
            print("  3. ❌ Git: user.name not configured")
    except:
        print("  3. ❌ Git: not available")

    # Show system user
    import getpass
    print(f"  4. ✅ System: {getpass.getuser()}")

    return 0

def owner_set(name: str):
    """Set persistent owner."""
    from pathlib import Path

    # Create .otk directory if it doesn't exist
    otk_dir = Path(".otk")
    otk_dir.mkdir(exist_ok=True)

    # Write owner file
    owner_file = otk_dir / ".owner"
    owner_file.write_text(name)

    print(f"✅ Owner set to: {name}")
    print(f"   Saved to: .otk/.owner")
    print("\nNote: This overrides git config but not OTK_OWNER environment variable.")

    return 0

def plan_command(args):
    """Handle 'otk plan' command - wrapper around otk-new."""
    import sys
    from .cli_new import handle_plan_command
    from .owner import resolve_owner

    title = " ".join(args.title) if args.title else ""
    owner = resolve_owner()
    ready = args.ready if hasattr(args, 'ready') else False

    return handle_plan_command(title, owner, ready)

def spec_command(args):
    """Handle 'otk spec' command - wrapper around otk-new."""
    import sys
    from .cli_new import handle_spec_command
    from .owner import resolve_owner

    title = " ".join(args.title) if args.title else ""
    owner = resolve_owner()
    plan_id = args.plan if hasattr(args, 'plan') else None

    return handle_spec_command(title, owner, plan_id)

def exec_command(args):
    """Handle 'otk exec' command - wrapper around otk-new."""
    from .cli_new import handle_execute_command
    from .owner import resolve_owner

    spec_id = args.spec if hasattr(args, 'spec') else None
    owner = resolve_owner()

    return handle_execute_command(owner, spec_id)

def scout_command(args):
    """Handle 'otk scout' command - generate implementation checklist."""
    from .scout import scout_spec

    if not args.spec:
        print("Usage: otk scout <SPEC-ID>")
        return 1

    return scout_spec(args.spec)

def orchestrator_watch():
    from .orchestrator import main
    sys.argv = ["orchestrator.py", "--watch"]
    main()

def main():
    """Main CLI entry point for otk command."""
    parser = argparse.ArgumentParser(
        description="Orchestrator Toolkit CLI",
        prog="otk"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add subcommands
    subparsers.add_parser("task-new", help="Create a new task")
    subparsers.add_parser("plan-new", help="Create a new plan")
    subparsers.add_parser("orchestrator-once", help="Run orchestrator once")
    subparsers.add_parser("orchestrate", help="Run PLAN → SPEC orchestration")
    plan_sum = subparsers.add_parser("plan-summarize", help="Summarize a plan")
    plan_sum.add_argument("plan_id", help="Plan ID to summarize")

    # New clean subcommands
    plan_parser = subparsers.add_parser("plan", help="Create a new PLAN")
    plan_parser.add_argument("title", nargs="*", help="Plan title")
    plan_parser.add_argument("--ready", action="store_true", help="Create with status=ready")

    spec_parser = subparsers.add_parser("spec", help="Create a new SPEC")
    spec_parser.add_argument("title", nargs="*", help="Spec title")
    spec_parser.add_argument("--plan", help="Parent PLAN ID")

    exec_parser = subparsers.add_parser("exec", help="Execute a SPEC")
    exec_parser.add_argument("spec", nargs="?", help="SPEC ID to execute")

    scout_parser = subparsers.add_parser("scout", help="Generate implementation checklist from SPEC")
    scout_parser.add_argument("spec", help="SPEC ID to scout")

    # Owner subcommands
    owner_parser = subparsers.add_parser("owner", help="Manage owner settings")
    owner_subparsers = owner_parser.add_subparsers(dest="owner_command", help="Owner commands")
    owner_subparsers.add_parser("who", help="Show current owner resolution")
    owner_set_parser = owner_subparsers.add_parser("set", help="Set persistent owner")
    owner_set_parser.add_argument("name", help="Owner name to set")

    args = parser.parse_args()

    if args.command == "task-new":
        task_new()
    elif args.command == "plan-new":
        plan_new()
    elif args.command == "orchestrator-once":
        orchestrator_once()
    elif args.command == "orchestrate":
        orchestrate()
    elif args.command == "plan-summarize":
        # Pass the plan_id to plan_summarize
        sys.argv = ["otk", "plan-summarize", args.plan_id]
        plan_summarize()
    elif args.command == "plan":
        return plan_command(args)
    elif args.command == "spec":
        return spec_command(args)
    elif args.command == "exec":
        return exec_command(args)
    elif args.command == "scout":
        return scout_command(args)
    elif args.command == "owner":
        if args.owner_command == "who":
            owner_who()
        elif args.owner_command == "set":
            owner_set(args.name)
        else:
            owner_parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1

    return 0
