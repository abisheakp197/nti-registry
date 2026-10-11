"""Registration end-to-end."""


import json
from lib.entries import build_entry
from lib.signing import sign_payload
from api._handlers.register import handle_register




def _make_signed_entry(name="test-tool"):
    e = build_entry(
        name=name, version="0.1.0", description="A test tool",
        category="framework",
        repo_url="https://github.com/abisheakp197/langchain-nti",
        badge_url="https://nti-badge-svs1.vercel.app",
        nti_score=95,
    )
    return sign_payload(e)




def test_register_rejects_malformed_json(temp_registry_store):
    status, headers, body = handle_register("not json")
    assert status == 400
    assert b"invalid_json" in body




def test_register_rejects_missing_entry(temp_registry_store):
    status, headers, body = handle_register('{"foo": "bar"}')
    assert status == 400
    assert b"missing_entry" in body




def test_register_rejects_hash_tamper(temp_registry_store):
    entry = _make_signed_entry()
    entry["nti_score"] = 0  # tamper after signing
    body = json.dumps({"entry": entry, "strict": False})
    status, headers, payload = handle_register(body)
    assert status == 400
    assert b"hash_mismatch" in payload
