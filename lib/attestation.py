"""Signed registry response builders."""

from datetime import UTC, datetime
from typing import Any


def build_list_response(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "spec": "NTI-Registry-List/1",
        "issued_at": datetime.now(UTC).isoformat(),
        "count": len(entries),
        "entries": entries,
    }


def build_search_response(query: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "spec": "NTI-Registry-Search/1",
        "issued_at": datetime.now(UTC).isoformat(),
        "query": query,
        "count": len(entries),
        "entries": entries,
    }
