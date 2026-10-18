"""GET /api/list — full list of registry entries."""

import asyncio
import json
from typing import Any

from lib.attestation import build_list_response
from lib.db import hgetall


async def _list(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    raw = await hgetall("nti:registry:entries")
    entries: list[dict[str, Any]] = []
    for v in raw.values():
        try:
            val = json.loads(v)
            if isinstance(val, dict):
                entries.append(val)
        except (json.JSONDecodeError, TypeError):
            continue

    # Sort newest first
    entries.sort(key=lambda e: str(e.get("registered_at", "")), reverse=True)

    # Optional limit validation
    limit_str = query.get("limit")
    if limit_str and limit_str.isdigit():
        limit_val = max(1, min(int(limit_str), 1000))
        entries = entries[:limit_val]

    return (200, {"Content-Type": "application/json"},
            json.dumps(build_list_response(entries), indent=2).encode("utf-8"))


def handle_list(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    return asyncio.run(_list(query))
