"""POST /api/register — submit a signed registry entry."""


import json
import asyncio
from datetime import datetime, timezone


from lib.db import hset, hget
from lib.entries import validate_entry
from lib.signing import verify_integrity
from lib.verifier import cross_verify




async def _register(body_raw: str) -> tuple:
    try:
        body = json.loads(body_raw)
    except Exception:
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_json"}).encode("utf-8"))

    if not isinstance(body, dict):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "missing_entry"}).encode("utf-8"))

    entry = body.get("entry")
    if not isinstance(entry, dict):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "missing_entry"}).encode("utf-8"))


    # 1. Structural validation
    try:
        validate_entry(entry)
    except ValueError as e:
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_entry", "detail": str(e)}).encode("utf-8"))


    # 2. Hash integrity (signature bound to payload)
    if not verify_integrity(entry):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "hash_mismatch"}).encode("utf-8"))


    # 3. Cross-verify against the live badge node
    verification = await cross_verify(entry)
    entry["cross_verified"] = verification["ok"]
    entry["cross_verified_at"] = datetime.now(timezone.utc).isoformat()


    # 4. Reject if cross-verify failed AND no explicit override
    strict = body.get("strict", True)
    if strict and not verification["ok"]:
        return (400, {"Content-Type": "application/json"},
                json.dumps({
                    "error": "cross_verification_failed",
                    "detail": verification,
                }).encode("utf-8"))


    # 5. Store
    await hset("nti:registry:entries", entry["id"], json.dumps(entry))


    return (200, {"Content-Type": "application/json"},
            json.dumps({
                "status": "registered",
                "id": entry["id"],
                "cross_verified": verification["ok"],
                "verification": verification,
            }).encode("utf-8"))




def handle_register(body_raw: str) -> tuple:
    return asyncio.run(_register(body_raw))
