"""Announce this registry node to upstream registry nodes for federation."""


import asyncio
import httpx
from typing import List




async def announce_to_peer(peer_url: str, node_url: str, node_name: str, timeout: float = 10.0) -> dict:
    """Announce this registry node to a peer registry."""
    url = peer_url.rstrip("/") + "/api/federation/register"
    payload = {"url": node_url, "name": node_name, "kind": "registry"}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=payload)
            if r.status_code == 200:
                return {"peer": peer_url, "ok": True, "response": r.json()}
            return {"peer": peer_url, "ok": False, "status": r.status_code}
    except Exception as e:
        return {"peer": peer_url, "ok": False, "error": str(e)}




async def announce_to_all(peer_urls: List[str], node_url: str, node_name: str) -> list:
    if not peer_urls:
        return []
    tasks = [announce_to_peer(p, node_url, node_name) for p in peer_urls]
    return await asyncio.gather(*tasks)
