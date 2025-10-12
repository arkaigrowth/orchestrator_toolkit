from __future__ import annotations
from typing import Dict, Any
from urllib import request, error
import json
from .settings import OrchSettings

def add_memory(settings: OrchSettings, project: str, org: str, content: str, metadata: Dict[str, Any] | None=None) -> Dict[str, Any]:
    if not settings.mem0_enabled or not settings.mem0_api_key:
        return {"ok": False, "skipped": "mem0 disabled"}
    url = f"{settings.mem0_api_url.rstrip('/')}/memories"
    payload = {"project": project, "org": org, "content": content, "metadata": metadata or {}}
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.mem0_api_key}",
    }, method="POST")
    try:
        with request.urlopen(req, timeout=5) as resp:
            return {"ok": True, "status": resp.status}
    except error.URLError as e:
        return {"ok": False, "error": str(e)}
