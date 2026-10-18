"""Malformed input never crashes."""

from api.index import route


def test_register_empty_body(temp_registry_store):
    status, _, _ = route("POST", "/api/register", {}, "")
    assert status == 400


def test_register_garbage_body(temp_registry_store):
    status, _, _ = route("POST", "/api/register", {}, "{{{{")
    assert status == 400


def test_register_null_body(temp_registry_store):
    status, _, _ = route("POST", "/api/register", {}, "null")
    assert status == 400


def test_sync_missing_from(temp_registry_store):
    status, _, _ = route("GET", "/api/sync", {}, "")
    assert status == 400


def test_verify_missing_id(temp_registry_store):
    status, _, _ = route("GET", "/api/verify", {}, "")
    assert status == 400
