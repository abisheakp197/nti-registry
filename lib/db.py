"""Database abstraction. User brings their own DB. Same pattern as nti-badge."""


import os
import json
import asyncio
from pathlib import Path
from typing import Optional, List




BACKEND: Optional[str] = None
_redis_client = None
_file_locks = {}
def _get_local_store_dir() -> Path:
    if "NTI_LOCAL_STORE" in os.environ:
        return Path(os.environ["NTI_LOCAL_STORE"])
    # If VERCEL environment or default store not writable, fallback to /tmp/.nti-registry-data
    default_dir = Path(".nti-registry-data")
    if os.environ.get("VERCEL"):
        return Path("/tmp/.nti-registry-data")
    return default_dir


def _get_file_lock() -> asyncio.Lock:
    loop = asyncio.get_running_loop()
    if loop not in _file_locks:
        _file_locks[loop] = asyncio.Lock()
    return _file_locks[loop]




def _detect_backend() -> str:
    if os.environ.get("KV_URL") or os.environ.get("REDIS_URL"):
        return "redis"
    return "file"




def get_backend() -> str:
    global BACKEND
    if BACKEND is None:
        BACKEND = _detect_backend()
    return BACKEND




def _redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
            url = os.environ.get("KV_URL") or os.environ.get("REDIS_URL")
            _redis_client = aioredis.from_url(url, decode_responses=True)
        except Exception:
            _redis_client = None
    return _redis_client




async def _file_path(namespace: str) -> Path:
    store_dir = _get_local_store_dir()
    try:
        store_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fallback to /tmp if default directory isn't writable
        store_dir = Path("/tmp/.nti-registry-data")
        store_dir.mkdir(parents=True, exist_ok=True)
    return store_dir / f"{namespace.replace(':', '_')}.json"




async def hset(namespace: str, key: str, value: str) -> None:
    if get_backend() == "redis":
        r = _redis()
        if r:
            await r.hset(namespace, key, value)
            return
    async with _get_file_lock():
        path = await _file_path(namespace)
        data = {}
        if path.exists():
            try:
                data = json.loads(path.read_text())
            except Exception:
                data = {}
        data[key] = value
        path.write_text(json.dumps(data, indent=2))




async def hget(namespace: str, key: str) -> Optional[str]:
    if get_backend() == "redis":
        r = _redis()
        if r:
            return await r.hget(namespace, key)
    try:
        path = await _file_path(namespace)
        if not path.exists():
            return None
        return json.loads(path.read_text()).get(key)
    except Exception:
        return None




async def hgetall(namespace: str) -> dict:
    if get_backend() == "redis":
        r = _redis()
        if r:
            return await r.hgetall(namespace)
    try:
        path = await _file_path(namespace)
        if not path.exists():
            return {}
        return json.loads(path.read_text())
    except Exception:
        return {}




async def hdel(namespace: str, key: str) -> None:
    if get_backend() == "redis":
        r = _redis()
        if r:
            await r.hdel(namespace, key)
            return
    async with _get_file_lock():
        path = await _file_path(namespace)
        if path.exists():
            try:
                data = json.loads(path.read_text())
                data.pop(key, None)
                path.write_text(json.dumps(data, indent=2))
            except Exception:
                pass




def backend_info() -> dict:
    return {
        "backend": get_backend(),
        "note": "Bring your own DB via KV_URL or REDIS_URL. Otherwise file-based fallback.",
    }
