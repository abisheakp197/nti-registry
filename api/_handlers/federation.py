"""Federation endpoints. Any registry can mirror any other."""

import asyncio
import json
import os
from datetime import UTC, datetime
from typing import Any

from lib.db import hgetall, hset


def _node_info() -> dict[str, str]:
    return {
        "url": os.environ.get("NTI_REGISTRY_URL", ""),
        "name": os.environ.get("NTI_REGISTRY_NAME", "nti-registry"),
        "contact": os.environ.get("NTI_REGISTRY_CONTACT", ""),
    }


def handle_federation_get() -> tuple[int, dict[str, str], bytes]:
    node = _node_info()

    peers_raw = asyncio.run(hgetall("nti:registry:peers"))
    peers: list[dict[str, Any]] = []
    for v in peers_raw.values():
        try:
            val = json.loads(v)
            if isinstance(val, dict):
                peers.append(val)
        except (json.JSONDecodeError, TypeError):
            continue

    manifest = {
        "spec": "NTI-Registry-Federation/1",
        "issued_at": datetime.now(UTC).isoformat(),
        "node": node,
        "endpoints": {
            "register": "POST /api/register",
            "list": "GET /api/list",
            "verify": "GET /api/verify?id=...",
            "search": "GET /api/search?q=...&category=...",
            "federation": "GET /api/federation",
            "peer_register": "POST /api/federation/register",
            "sync": "GET /api/sync?from=...",
            "stats": "GET /api/stats",
            "health": "GET /api/health",
        },
        "peers": peers,
        "mirror_howto": {
            "step_1": "Clone github.com/abisheakp197/nti-registry",
            "step_2": "Deploy to Vercel (or any Python serverless platform)",
            "step_3": "Attach KV/Redis via KV_URL env var",
            "step_4": "POST to /api/federation/register on peers to announce",
        },
        "neutrality": (
            "No central authority. Every entry is signed by its owner. "
            "Cross-verified against a live badge node. Federated. "
            "Offline-verifiable forever."
        ),
    }

    return (200, {"Content-Type": "application/json"},
            json.dumps(manifest, indent=2).encode("utf-8"))


async def _register_peer(body_raw: str) -> tuple[int, dict[str, str], bytes]:
    try:
        body = json.loads(body_raw)
    except (json.JSONDecodeError, TypeError):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_json"}).encode("utf-8"))

    if not isinstance(body, dict):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_payload"}).encode("utf-8"))

    url = str(body.get("url") or "").strip().rstrip("/")
    name = str(body.get("name", "unnamed-peer"))
    kind = str(body.get("kind", "registry"))

    if not url or not url.startswith(("http://", "https://")):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_url"}).encode("utf-8"))

    entry = {
        "url": url,
        "name": name,
        "kind": kind,
        "registered_at": datetime.now(UTC).isoformat(),
    }

    await hset("nti:registry:peers", url, json.dumps(entry))

    return (200, {"Content-Type": "application/json"},
            json.dumps({"status": "peer_registered", "peer": entry}).encode("utf-8"))


def handle_federation_post(body_raw: str) -> tuple[int, dict[str, str], bytes]:
    return asyncio.run(_register_peer(body_raw))
