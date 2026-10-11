"""Signed registry response builders."""


import json
import hashlib
from datetime import datetime, timezone




def build_list_response(entries: list) -> dict:
    return {
        "spec": "NTI-Registry-List/1",
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "count": len(entries),
        "entries": entries,
    }




def build_search_response(query: str, entries: list) -> dict:
    return {
        "spec": "NTI-Registry-Search/1",
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "count": len(entries),
        "entries": entries,
    }
