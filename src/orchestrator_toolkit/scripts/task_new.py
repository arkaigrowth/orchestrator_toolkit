from pathlib import Path
from ..settings import OrchSettings
from ..utils import now_iso
from ..id_alloc import next_numeric
import argparse
import sys

def next_task_id(tasks_dir: Path) -> str:
    """Get next task ID by scanning directory."""
    return next_numeric("T", tasks_dir)

def create_task(title: str, owner: str = "unknown") -> Path:
    """Create new task file in artifact_root/tasks/."""
    s = OrchSettings.load()
    task_id = next_task_id(s.tasks_dir)

    template = Path(".claude/templates/task.md")
    if not template.exists():
        # Auto-create a sensible default template if missing
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_text(
            "---\n"
            "id: T-${ID}\n"
            "title: ${TITLE}\n"
            "owner: ${OWNER}\n"
            "status: assigned   # (new|assigned|in-progress|blocked|done)\n"
            "created: ${DATE}\n"
            "---\n\n"
            "## Goal\n\n${TITLE}\n\n## Notes\n\n- Add constraints/notes here.\n",
            encoding="utf-8"
        )

    # Read template and replace placeholders
    content = template.read_text()
    content = content.replace("${ID}", task_id)
    content = content.replace("${TITLE}", title)
    content = content.replace("${OWNER}", owner)
    content = content.replace("${DATE}", now_iso())

    # Write task file
    out = s.tasks_dir / f"T-{task_id}.md"
    out.write_text(content, encoding="utf-8")
    return out

def main():
    """CLI entry point with proper error handling and exit codes."""
    try:
        parser = argparse.ArgumentParser(description="Create a new task")
        parser.add_argument("title", help="Task title")
        parser.add_argument("--owner", default="unknown", help="Task owner")
        args = parser.parse_args()

        out = create_task(args.title, args.owner)
        print(out)
        return 0
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())