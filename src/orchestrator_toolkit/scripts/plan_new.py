from pathlib import Path
from ..settings import OrchSettings
from ..utils import now_iso
from ..id_alloc import next_numeric
import argparse
import sys

def next_plan_id(plans_dir: Path) -> str:
    """Get next plan ID by scanning directory."""
    return next_numeric("P", plans_dir)

def create_plan(title: str, owner: str = "unknown", task_id: str = "") -> Path:
    """Create new plan file in artifact_root/plans/."""
    s = OrchSettings.load()
    plan_id = next_plan_id(s.plans_dir)

    template = Path(".claude/templates/plan.md")
    if not template.exists():
        # Auto-create a sensible default template if missing
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_text(
            "---\n"
            "id: P-${ID}\n"
            "task: ${TASK_ID}\n"
            "title: ${TITLE}\n"
            "owner: ${OWNER}\n"
            "created: ${DATE}\n"
            "status: draft\n"
            "---\n\n"
            "## Overview\n\n(Scaffolded by orchestrator.)\n\n"
            "## Steps\n\n1. Draft approach\n2. Identify inputs\n3. Produce deliverable\n\n"
            "## References\n\n- (add paths / URLs)\n",
            encoding="utf-8"
        )

    # Read template and replace placeholders
    content = template.read_text()
    content = content.replace("${ID}", plan_id)
    content = content.replace("${TITLE}", title)
    content = content.replace("${OWNER}", owner)
    content = content.replace("${TASK_ID}", task_id)
    content = content.replace("${DATE}", now_iso())

    # Write plan file
    out = s.plans_dir / f"P-{plan_id}.md"
    out.write_text(content, encoding="utf-8")
    return out

def main():
    """CLI entry point with proper error handling and exit codes."""
    try:
        parser = argparse.ArgumentParser(description="Create a new plan")
        parser.add_argument("title", help="Plan title")
        parser.add_argument("--owner", default="unknown", help="Plan owner")
        parser.add_argument("--task", default="", help="Associated task ID")
        args = parser.parse_args()

        out = create_plan(args.title, args.owner, args.task)
        print(out)
        return 0
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())