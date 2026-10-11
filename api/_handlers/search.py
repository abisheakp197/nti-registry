"""GET /api/search?q=...&category=...&min_score=... — filter entries."""


import json
import asyncio


from lib.db import hgetall
from lib.attestation import build_search_response




async def _search(query: dict) -> tuple:
    q = (query.get("q") or "").lower().strip()
    category = query.get("category", "").strip()
    min_score = query.get("min_score", "")
    max_score = query.get("max_score", "")


    raw = await hgetall("nti:registry:entries")
    entries = []
    for v in raw.values():
        try:
            entries.append(json.loads(v))
        except Exception:
            continue


    # Filters
    def matches(e: dict) -> bool:
        if category and e.get("category") != category:
            return False
        if q:
            haystack = (e.get("name", "") + " " + e.get("description", "")).lower()
            if q not in haystack:
                return False
        if min_score.isdigit() and e.get("nti_score", 0) < int(min_score):
            return False
        if max_score.isdigit() and e.get("nti_score", 0) > int(max_score):
            return False
        return True


    results = [e for e in entries if matches(e)]
    results.sort(key=lambda e: e.get("nti_score", 0), reverse=True)


    return (200, {"Content-Type": "application/json"},
            json.dumps(build_search_response(q, results), indent=2).encode("utf-8"))




def handle_search(query: dict) -> tuple:
    return asyncio.run(_search(query))
