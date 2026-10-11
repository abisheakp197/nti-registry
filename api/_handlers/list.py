"""GET /api/list — full list of registry entries."""


import json
import asyncio


from lib.db import hgetall
from lib.attestation import build_list_response




async def _list(query: dict) -> tuple:
    raw = await hgetall("nti:registry:entries")
    entries = []
    for v in raw.values():
        try:
            entries.append(json.loads(v))
        except Exception:
            continue


    # Sort newest first
    entries.sort(key=lambda e: e.get("registered_at", ""), reverse=True)


    # Optional limit
    limit = query.get("limit")
    if limit and limit.isdigit():
        entries = entries[: int(limit)]


    return (200, {"Content-Type": "application/json"},
            json.dumps(build_list_response(entries), indent=2).encode("utf-8"))




def handle_list(query: dict) -> tuple:
    return asyncio.run(_list(query))
