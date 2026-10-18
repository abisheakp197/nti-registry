"""GET /api/sync?from=<peer_url> — pull entries from a peer registry."""

import asyncio
import json
from datetime import UTC, datetime

import httpx

from lib.db import hget, hset
from lib.signing import verify_integrity


async def _sync(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    peer = (query.get("from") or "").strip().rstrip("/")
    if not peer or not peer.startswith(("http://", "https://")):
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
    except (httpx.HTTPError, ValueError):
        return (502, {"Content-Type": "application/json"},
                json.dumps({"error": "peer_error"}).encode("utf-8"))

    if not isinstance(data, dict):
        return (502, {"Content-Type": "application/json"},
                json.dumps({"error": "peer_invalid_response"}).encode("utf-8"))

    entries = data.get("entries")
    if not isinstance(entries, list):
        entries = []

    imported = 0
    skipped = 0
    rejected = 0

    for entry in entries:
        if not isinstance(entry, dict) or "id" not in entry:
            rejected += 1
            continue

        entry_id = str(entry["id"])

        # Skip if already have it
        existing = await hget("nti:registry:entries", entry_id)
        if existing:
            skipped += 1
            continue

        # Reject if hash integrity fails
        if not verify_integrity(entry):
            rejected += 1
            continue

        # Tag as imported
        entry["imported_from"] = peer
        entry["imported_at"] = datetime.now(UTC).isoformat()
        await hset("nti:registry:entries", entry_id, json.dumps(entry))
        imported += 1

    return (200, {"Content-Type": "application/json"},
            json.dumps({
                "status": "sync_complete",
                "peer": peer,
                "imported": imported,
                "skipped": skipped,
                "rejected": rejected,
            }, indent=2).encode("utf-8"))


def handle_sync(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    return asyncio.run(_sync(query))
