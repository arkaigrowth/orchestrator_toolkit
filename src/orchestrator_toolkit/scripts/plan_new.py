"""
Legacy plan-new command - Back-compat shim.

Delegates to new ULID-based plan creation (cli_new.py) while maintaining
legacy CLI interface (--owner, --task flags).
"""
from pathlib import Path
import argparse
import sys

def create_plan(title: str, owner: str = "unknown", task_id: str = "") -> Path:
    """
    Create new plan file using new ULID-based system.

    This is a back-compat shim that delegates to cli_new.create_plan_file()
    while maintaining the legacy API.

    Args:
        title: Plan title
        owner: Owner name (defaults to "unknown")
        task_id: Associated task ID (deprecated, ignored in new system)

    Returns:
        Path to created plan file
    """
    from ..cli_new import create_plan_file
    from ..owner import resolve_owner

    # Use explicit owner or resolve from environment
    final_owner = owner if owner != "unknown" else resolve_owner()

    # Delegate to new ULID-based system
    out = create_plan_file(title, final_owner)
    return out

def main():
    """CLI entry point with proper error handling and exit codes."""
    try:
        parser = argparse.ArgumentParser(description="Create a new plan (legacy command)")
        parser.add_argument("title", help="Plan title")
        parser.add_argument("--owner", default="unknown", help="Plan owner")
        parser.add_argument("--task", default="", help="Associated task ID (deprecated)")
        args = parser.parse_args()

        if args.task:
            print("⚠️  Note: --task flag is deprecated in new PLAN/SPEC model", file=sys.stderr)

        out = create_plan(args.title, args.owner, args.task)
        print(out)
        return 0
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())