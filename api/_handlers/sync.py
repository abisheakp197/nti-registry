"""GET /api/sync?from=<peer_url> — pull entries from a peer registry."""


import json
import asyncio
from datetime import datetime, timezone


import httpx


from lib.db import hget, hset
from lib.signing import verify_integrity




async def _sync(query: dict) -> tuple:
    peer = (query.get("from") or "").strip().rstrip("/")
    if not peer or not peer.startswith("http"):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "missing_or_invalid_from"}).encode("utf-8"))


    url = peer + "/api/list"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return (502, {"Content-Type": "application/json"},
                        json.dumps({"error": "peer_unreachable", "status": r.status_code}).encode("utf-8"))
            data = r.json()
    except Exception as e:
        return (502, {"Content-Type": "application/json"},
                json.dumps({"error": "peer_error", "detail": str(e)}).encode("utf-8"))


    entries = data.get("entries") or []
    imported = 0
    skipped = 0
    rejected = 0


    for entry in entries:
        if not isinstance(entry, dict) or "id" not in entry:
            rejected += 1
            continue


        # Skip if already have it
        existing = await hget("nti:registry:entries", entry["id"])
        if existing:
            skipped += 1
            continue


        # Reject if hash integrity fails
        if not verify_integrity(entry):
            rejected += 1
            continue


        # Tag as imported
        entry["imported_from"] = peer
        entry["imported_at"] = datetime.now(timezone.utc).isoformat()
        await hset("nti:registry:entries", entry["id"], json.dumps(entry))
        imported += 1


    return (200, {"Content-Type": "application/json"},
            json.dumps({
                "status": "sync_complete",
                "peer": peer,
                "imported": imported,
                "skipped": skipped,
                "rejected": rejected,
            }, indent=2).encode("utf-8"))




def handle_sync(query: dict) -> tuple:
    return asyncio.run(_sync(query))
