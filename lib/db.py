"""Database abstraction. User brings their own DB. Same pattern as nti-badge."""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any

BACKEND: str | None = None
_redis_client: Any = None
_file_locks: dict[asyncio.AbstractEventLoop, asyncio.Lock] = {}


def _get_local_store_dir() -> Path:
    if "NTI_LOCAL_STORE" in os.environ:
        return Path(os.environ["NTI_LOCAL_STORE"])
    default_dir = Path(".nti-registry-data")
    if os.environ.get("VERCEL"):
        return Path(tempfile.gettempdir()) / ".nti-registry-data"
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


def _redis() -> Any:
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis  # type: ignore[import-not-found]

            url = os.environ.get("KV_URL") or os.environ.get("REDIS_URL") or ""
            if url:
                _redis_client = aioredis.from_url(url, decode_responses=True)
        except Exception:  # noqa: BLE001
            _redis_client = None
    return _redis_client


async def _file_path(namespace: str) -> Path:
    store_dir = _get_local_store_dir()
    try:
        store_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        store_dir = Path(tempfile.gettempdir()) / ".nti-registry-data"
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
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                data = {}
        data[key] = value
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


async def hget(namespace: str, key: str) -> str | None:
    if get_backend() == "redis":
        r = _redis()
        if r:
            res: str | None = await r.hget(namespace, key)
            return res
    try:
        path = await _file_path(namespace)
        if not path.exists():
            return None
        content = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(content, dict):
            val = content.get(key)
            return str(val) if val is not None else None
        return None
    except (json.JSONDecodeError, OSError):
        return None


async def hgetall(namespace: str) -> dict[str, str]:
    if get_backend() == "redis":
        r = _redis()
        if r:
            res: dict[str, str] = await r.hgetall(namespace)
            return res
    try:
        path = await _file_path(namespace)
        if not path.exists():
            return {}
        content = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(content, dict):
            return {str(k): str(v) for k, v in content.items()}
        return {}
    except (json.JSONDecodeError, OSError):
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
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data.pop(key, None)
                    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except (json.JSONDecodeError, OSError):
                pass


def backend_info() -> dict[str, str]:
    return {
        "backend": get_backend(),
        "note": "Bring your own DB via KV_URL or REDIS_URL. Otherwise file-based fallback.",
    }
