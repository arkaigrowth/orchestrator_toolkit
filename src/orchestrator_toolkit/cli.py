from __future__ import annotations
import argparse, sys, subprocess

def _run(cmd: str) -> str:
    p = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    return p.stdout.strip()

def task_new():
    """Delegate to Python-based task creation."""
    from .scripts.task_new import main
    main()

def plan_new():
    """Delegate to Python-based plan creation."""
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

def orchestrator_watch():
    from .orchestrator import main
    sys.argv = ["orchestrator.py", "--watch"]
    main()
