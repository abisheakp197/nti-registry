"""DB layer."""


import asyncio
from lib import db




def test_backend_file_when_no_env(clean_env=None):
    db.BACKEND = None
    assert db.get_backend() in ("file", "redis")




def test_hset_hget_roundtrip(temp_registry_store):
    db.BACKEND = None
    async def flow():
        await db.hset("test", "key1", "value1")
        v = await db.hget("test", "key1")
        assert v == "value1"
    asyncio.run(flow())




def test_hget_missing_returns_none(temp_registry_store):
    db.BACKEND = None
    assert asyncio.run(db.hget("test", "nope")) is None




def test_hgetall_empty(temp_registry_store):
    db.BACKEND = None
    assert asyncio.run(db.hgetall("test")) == {}




def test_hdel(temp_registry_store):
    db.BACKEND = None
    async def flow():
        await db.hset("test", "k", "v")
        await db.hdel("test", "k")
        assert await db.hget("test", "k") is None
    asyncio.run(flow())
