"""GET /api/stats — public counters."""

import asyncio
import json
from datetime import UTC, datetime

from lib.db import hgetall


async def _stats() -> tuple[int, dict[str, str], bytes]:
    entries_raw = await hgetall("nti:registry:entries")
    peers_raw = await hgetall("nti:registry:peers")

    categories: dict[str, int] = {}
    verified_count = 0
    total_score = 0
    total_entries = 0

    for v in entries_raw.values():
        try:
            e = json.loads(v)
            if not isinstance(e, dict):
                continue
        except (json.JSONDecodeError, TypeError):
            continue
        total_entries += 1
        cat = str(e.get("category", "unknown"))
        categories[cat] = categories.get(cat, 0) + 1
        if e.get("cross_verified"):
            verified_count += 1
        score = e.get("nti_score", 0)
        if isinstance(score, int):
            total_score += score

    avg_score = int(total_score / total_entries) if total_entries > 0 else 0

    return (200, {"Content-Type": "application/json"},
            json.dumps({
                "spec": "NTI-Registry-Stats/1",
                "issued_at": datetime.now(UTC).isoformat(),
                "total_entries": total_entries,
                "total_peers": len(peers_raw),
                "cross_verified_count": verified_count,
                "average_score": avg_score,
                "by_category": categories,
            }, indent=2).encode("utf-8"))


def handle_stats() -> tuple[int, dict[str, str], bytes]:
    return asyncio.run(_stats())
