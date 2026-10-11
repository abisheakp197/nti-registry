"""Federation endpoints. Any registry can mirror any other."""


import json
import asyncio
import os
from datetime import datetime, timezone


from lib.db import hset, hgetall




def _node_info() -> dict:
    return {
        "url": os.environ.get("NTI_REGISTRY_URL", ""),
        "name": os.environ.get("NTI_REGISTRY_NAME", "nti-registry"),
        "contact": os.environ.get("NTI_REGISTRY_CONTACT", ""),
    }




def handle_federation_get() -> tuple:
    node = _node_info()


    peers_raw = asyncio.run(hgetall("nti:registry:peers"))
    peers = []
    for v in peers_raw.values():
        try:
            peers.append(json.loads(v))
        except Exception:
            continue


    manifest = {
        "spec": "NTI-Registry-Federation/1",
        "issued_at": datetime.now(timezone.utc).isoformat(),
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




async def _register_peer(body_raw: str) -> tuple:
    try:
        body = json.loads(body_raw)
    except Exception:
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_json"}).encode("utf-8"))


    url = (body.get("url") or "").strip().rstrip("/")
    name = body.get("name", "unnamed-peer")
    kind = body.get("kind", "registry")


    if not url or not url.startswith("http"):
        return (400, {"Content-Type": "application/json"},
                json.dumps({"error": "invalid_url"}).encode("utf-8"))


    entry = {
        "url": url,
        "name": name,
        "kind": kind,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }


    await hset("nti:registry:peers", url, json.dumps(entry))


    return (200, {"Content-Type": "application/json"},
            json.dumps({"status": "peer_registered", "peer": entry}).encode("utf-8"))




def handle_federation_post(body_raw: str) -> tuple:
    return asyncio.run(_register_peer(body_raw))
