"""Hostile input and concurrency tests for API endpoints."""

import json
import threading

from api.index import route


def test_concurrent_health_requests():
    """Ensure 100+ concurrent health requests execute without errors."""
    results = []

    def make_request():
        status, _headers, body = route("GET", "/api/health", {}, "")
        results.append((status, body))

    threads = [threading.Thread(target=make_request) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 100
    for status, body in results:
        assert status == 200
        assert b"ok" in body


def test_search_extreme_scores(temp_registry_store):
    """Test search endpoint with negative and huge score boundaries."""
    status, _, payload = route("GET", "/api/search", {"min_score": "-10", "max_score": "999999"}, "")
    assert status == 200
    data = json.loads(payload)
    assert "entries" in data


def test_list_pagination_limit_bounds(temp_registry_store):
    """Test list endpoint with negative, zero, and huge limit values."""
    status1, _, _payload1 = route("GET", "/api/list", {"limit": "-5"}, "")
    assert status1 == 200

    status2, _, _payload2 = route("GET", "/api/list", {"limit": "0"}, "")
    assert status2 == 200

    status3, _, _payload3 = route("GET", "/api/list", {"limit": "999999"}, "")
    assert status3 == 200


def test_register_missing_required_fields(temp_registry_store):
    """Test registration missing individual required fields."""
    required_fields = ["spec", "id", "name", "version", "category", "repo_url", "badge_url", "nti_score", "registered_at"]
    base_entry = {
        "spec": "NTI-Registry-Entry/1",
        "id": "123",
        "name": "test",
        "version": "1.0",
        "category": "framework",
        "repo_url": "https://github.com/a/b",
        "badge_url": "https://badge.example.com",
        "nti_score": 100,
        "registered_at": "2026-01-01T00:00:00Z",
    }

    for field in required_fields:
        entry = dict(base_entry)
        entry.pop(field)
        body = json.dumps({"entry": entry})
        status, _, payload = route("POST", "/api/register", {}, body)
        assert status == 400
        assert b"invalid_entry" in payload or b"Missing required field" in payload
