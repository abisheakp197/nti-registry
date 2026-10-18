"""GET /api/search?q=...&category=...&min_score=... — filter entries."""

import asyncio
import json
from typing import Any

from lib.attestation import build_search_response
from lib.db import hgetall


async def _search(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    q = (query.get("q") or "").lower().strip()
    category = query.get("category", "").strip()
    min_score_str = query.get("min_score", "").strip()
    max_score_str = query.get("max_score", "").strip()

    min_score = int(min_score_str) if min_score_str.isdigit() else None
    max_score = int(max_score_str) if max_score_str.isdigit() else None

    raw = await hgetall("nti:registry:entries")
    entries: list[dict[str, Any]] = []
    for v in raw.values():
        try:
            val = json.loads(v)
            if isinstance(val, dict):
                entries.append(val)
        except (json.JSONDecodeError, TypeError):
            continue

    # Filters
    def matches(e: dict[str, Any]) -> bool:
        if category and e.get("category") != category:
            return False
        if q:
            haystack = (str(e.get("name", "")) + " " + str(e.get("description", ""))).lower()
            if q not in haystack:
                return False
        score = e.get("nti_score", 0)
        if isinstance(score, int):
            if min_score is not None and score < min_score:
                return False
            if max_score is not None and score > max_score:
                return False
        return True

    results = [e for e in entries if matches(e)]
    results.sort(key=lambda e: int(e.get("nti_score", 0)), reverse=True)

    return (200, {"Content-Type": "application/json"},
            json.dumps(build_search_response(q, results), indent=2).encode("utf-8"))


def handle_search(query: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    return asyncio.run(_search(query))
