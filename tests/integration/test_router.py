"""Router reaches each handler."""


import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from api.index import route




def test_health_route():
    status, headers, body = route("GET", "/api/health", {}, "")
    assert status == 200
    assert b"ok" in body




def test_list_route(temp_registry_store):
    status, headers, body = route("GET", "/api/list", {}, "")
    assert status == 200




def test_unknown_route():
    status, headers, body = route("GET", "/api/nope", {}, "")
    assert status == 404




def test_wrong_method_rejected():
    status, headers, body = route("DELETE", "/api/list", {}, "")
    assert status == 404
