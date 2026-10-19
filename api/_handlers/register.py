"""POST /api/register — submit a signed registry entry."""

import asyncio
import json
from datetime import UTC, datetime

from lib.db import hset
from lib.entries import validate_entry
from lib.signing import verify_integrity, verify_signature
from lib.verifier import cross_verify


async def _register(body_raw: str) -> tuple[int, dict[str, str], bytes]:
    try:
        body = json.loads(body_raw)
    except (json.JSONDecodeError, TypeError):
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
    except (ValueError, TypeError) as e:
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_entry", "detail": str(e)}).encode("utf-8"))

    # 2. Hash integrity & Dilithium5 signature validation
    if not verify_integrity(entry):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "hash_mismatch"}).encode("utf-8"))

    if not verify_signature(entry):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_signature"}).encode("utf-8"))

    # 3. Cross-verify against the live badge node
    try:
        verification = await cross_verify(entry)
    except ValueError as e:
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_url", "detail": str(e)}).encode("utf-8"))

    entry["cross_verified"] = verification["ok"]
    entry["cross_verified_at"] = datetime.now(UTC).isoformat()

    # 4. Reject if cross-verify failed AND no explicit override
    strict = body.get("strict", True)
    if strict and not verification["ok"]:
        return (400, {"Content-Type": "application/json"},
                json.dumps({
                    "error": "cross_verification_failed",
                    "detail": verification,
                }).encode("utf-8"))

    # 5. Store verified entry
    await hset("nti:registry:entries", str(entry["id"]), json.dumps(entry))

    return (200, {"Content-Type": "application/json"},
            json.dumps({
                "status": "registered",
                "id": entry["id"],
                "cross_verified": verification["ok"],
                "verification": verification,
            }).encode("utf-8"))


def handle_register(body_raw: str) -> tuple[int, dict[str, str], bytes]:
    return asyncio.run(_register(body_raw))
