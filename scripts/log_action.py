#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from datetime import datetime, timezone

def log(event: str, payload: dict):
    root = Path.cwd()
    exec_dir = root / "ai_docs" / "exec_logs"
    exec_dir.mkdir(parents=True, exist_ok=True)
    now_utc = datetime.now(timezone.utc)
    ts = now_utc.isoformat(timespec="seconds")
    day = now_utc.strftime("%Y%m%d")

    (exec_dir / "otk_exec.jsonl").open("a", encoding="utf-8").write(
        json.dumps({"event":event,"ts":ts,"payload":payload})+"\n"
    )
    (exec_dir / f"EXEC-{day}.md").open("a", encoding="utf-8").write(
        f"[{ts}] {event} {payload}\n"
    )

def main():
    if len(sys.argv) < 2:
        print("usage: log_action.py <event> [key=value ...]", file=sys.stderr)
        sys.exit(1)
    event = sys.argv[1]
    payload = {}
    for kv in sys.argv[2:]:
        if "=" in kv:
            k,v = kv.split("=",1)
            payload[k]=v
        else:
            payload[kv]=True
    log(event, payload)

if __name__ == "__main__":
    main()
