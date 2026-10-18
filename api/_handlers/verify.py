"""GET /api/verify?id=... — verify a single registry entry."""

import asyncio
import json

from lib.db import hget
from lib.signing import verify_integrity, verify_signature


async def _verify(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    entry_id = query.get("id", "").strip()
    if not entry_id:
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "missing_id"}).encode("utf-8"))

    raw = await hget("nti:registry:entries", entry_id)
    if not raw:
        return (404, {"Content-Type": "application/json"},
                json.dumps({"error": "not_found", "id": entry_id}).encode("utf-8"))

    try:
        entry = json.loads(raw)
        if not isinstance(entry, dict):
            return (404, {"Content-Type": "application/json"},
                    json.dumps({"error": "not_found", "id": entry_id}).encode("utf-8"))
    except (json.JSONDecodeError, TypeError):
        return (500, {"Content-Type": "application/json"},
                json.dumps({"error": "corrupted_entry"}).encode("utf-8"))

    return (200, {"Content-Type": "application/json"},
            json.dumps({
                "id": entry_id,
                "hash_ok": verify_integrity(entry),
                "signature_ok": verify_signature(entry),
                "cross_verified": entry.get("cross_verified", False),
                "spec": "NTI-Registry-Verify/1",
                "entry": entry,
            }, indent=2).encode("utf-8"))


def handle_verify(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    return asyncio.run(_verify(query))
