from __future__ import annotations
from typing import Any, Dict
from urllib import request, error
import json
from .settings import OrchSettings

def _post(url: str, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }, method="POST")
    try:
        with request.urlopen(req, timeout=5) as resp:
            return {"ok": True, "status": resp.status}
    except error.URLError as e:
        return {"ok": False, "error": str(e)}

def tasks_upsert(settings: OrchSettings, task: Dict[str, Any]) -> Dict[str, Any]:
    if not settings.archon_enabled or not settings.archon_api_key:
        return {"ok": False, "skipped": "archon disabled"}
    url = f"{settings.archon_base_url.rstrip('/')}/tasks.upsert"
    return _post(url, task, settings.archon_api_key)

def tasks_status(settings: OrchSettings, task_id: str, status: str) -> Dict[str, Any]:
    if not settings.archon_enabled or not settings.archon_api_key:
        return {"ok": False, "skipped": "archon disabled"}
    url = f"{settings.archon_base_url.rstrip('/')}/tasks.status"
    return _post(url, {"id": task_id, "status": status}, settings.archon_api_key)

def events_create(settings: OrchSettings, kind: str, message: str, meta: Dict[str, Any] | None=None) -> Dict[str, Any]:
    if not settings.archon_enabled or not settings.archon_api_key:
        return {"ok": False, "skipped": "archon disabled"}
    url = f"{settings.archon_base_url.rstrip('/')}/events.create"
    payload = {"kind": kind, "message": message, "meta": meta or {}}
    return _post(url, payload, settings.archon_api_key)
