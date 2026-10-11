"""GET /api/verify?id=... — verify a single registry entry."""


import json
import asyncio


from lib.db import hget
from lib.signing import verify_integrity, verify_signature




async def _verify(query: dict) -> tuple:
    entry_id = query.get("id", "")
    if not entry_id:
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "missing_id"}).encode("utf-8"))


    raw = await hget("nti:registry:entries", entry_id)
    if not raw:
        return (404, {"Content-Type": "application/json"},
                json.dumps({"error": "not_found", "id": entry_id}).encode("utf-8"))


    entry = json.loads(raw)


    return (200, {"Content-Type": "application/json"},
            json.dumps({
                "id": entry_id,
                "hash_ok": verify_integrity(entry),
                "signature_ok": verify_signature(entry),
                "cross_verified": entry.get("cross_verified", False),
                "spec": "NTI-Registry-Verify/1",
                "entry": entry,
            }, indent=2).encode("utf-8"))




def handle_verify(query: dict) -> tuple:
    return asyncio.run(_verify(query))
