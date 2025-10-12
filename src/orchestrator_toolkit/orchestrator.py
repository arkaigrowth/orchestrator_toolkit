from __future__ import annotations
import argparse, re, subprocess
from pathlib import Path
from typing import Optional
from .settings import OrchSettings
from .utils import now_iso, atomic_write
from .id_alloc import next_numeric
from .archon_adapter import tasks_upsert, events_create

TASK_FRONTMATTER = re.compile(r'^---[\s\S]*?id:\s*(T-\d+)[\s\S]*?title:\s*(.+?)\n[\s\S]*?owner:\s*(.+?)\n[\s\S]*?status:\s*(\w+)[\s\S]*?---', re.MULTILINE)

PLAN_TEMPLATE = """---
id: {plan_id}
task: {task_id}
title: PLAN for: {task_title}
owner: {owner}
created: {now}
status: draft
---

## Overview
(Scaffolded by orchestrator.)

## Steps
1. Draft approach
2. Identify inputs
3. Produce deliverable

## References
- (add paths / URLs)
"""

def _next_plan_id(plans_dir: Path) -> str:
    """Get next plan ID using directory-based ID generation."""
    return next_numeric("P", plans_dir)

def _scan_tasks(settings: OrchSettings):
    for p in sorted(settings.tasks_dir.glob("T-*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        m = TASK_FRONTMATTER.search(text)
        if not m:
            continue
        task_id, title, owner, status = m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
        yield p, task_id, title, owner, status

def _post_statusline(msg: str) -> None:
    hook = Path(".claude/hooks/post_to_statusline.sh")
    if hook.exists():
        subprocess.run([str(hook), msg], check=False)

def once() -> int:
    s = OrchSettings.load()  # Use centralized loader

    created = 0
    for path, task_id, title, owner, status in _scan_tasks(s):
        if status.lower() != "assigned":
            continue

        plan_id_num = _next_plan_id(s.plans_dir)
        plan_id = f"P-{plan_id_num}"
        plan_path = s.plans_dir / f"{plan_id}.md"
        atomic_write(plan_path, PLAN_TEMPLATE.format(
            plan_id=plan_id,
            task_id=task_id,
            task_title=title,
            owner=owner,
            now=now_iso()
        ))
        created += 1

        # Inform Archon (best-effort) and statusline
        tasks_upsert(s, {"id": task_id, "title": title, "owner": owner, "status": "assigned"})
        events_create(s, "log", f"Scaffolded {plan_id} for {task_id}", {"plan": str(plan_path)})
        _post_statusline(f"Next step: open {plan_path} (scaffolded for {task_id})")

    return created

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="poll every 5s")
    args = ap.parse_args()
    if not args.watch:
        c = once()
        print(f"created_plans={c}")
    else:
        import time
        while True:
            c = once()
            if c:
                print(f"created_plans={c}")
            time.sleep(5)

if __name__ == "__main__":
    main()
