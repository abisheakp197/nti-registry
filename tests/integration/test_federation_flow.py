"""Federation endpoints."""


import json
from api._handlers.federation import handle_federation_get, handle_federation_post




def test_federation_get_returns_manifest(temp_registry_store):
    status, headers, body = handle_federation_get()
    assert status == 200
    data = json.loads(body)
    assert data["spec"] == "NTI-Registry-Federation/1"
    assert "endpoints" in data




def test_federation_register_accepts_valid_peer(temp_registry_store):
    body = json.dumps({"url": "https://peer.example.com", "name": "peer-1", "kind": "registry"})
    status, headers, payload = handle_federation_post(body)
    assert status == 200
    data = json.loads(payload)
    assert data["status"] == "peer_registered"




def test_federation_register_rejects_bad_url(temp_registry_store):
    body = json.dumps({"url": "not-a-url", "name": "x"})
    status, headers, payload = handle_federation_post(body)
    assert status == 400




def test_federation_register_rejects_missing_url(temp_registry_store):
    body = json.dumps({"name": "x"})
    status, headers, payload = handle_federation_post(body)
    assert status == 400
