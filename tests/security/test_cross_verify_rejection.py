"""Cross-verification rejects mismatched scores."""


import json
from unittest.mock import patch

from api._handlers.register import handle_register
from lib.entries import build_entry
from lib.signing import sign_payload


def _signed(name="x"):
    e = build_entry(
        name=name, version="0.1.0", description="d", category="framework",
        repo_url="https://github.com/abisheakp197/langchain-nti",
        badge_url="https://nti-badge-svs1.vercel.app", nti_score=95,
    )
    return sign_payload(e)




def test_strict_mode_rejects_bad_cross_verify(temp_registry_store):
    entry = _signed()
    with patch("api._handlers.register.cross_verify",
               return_value={"ok": False, "reason": "score mismatch"}):
        body = json.dumps({"entry": entry, "strict": True})
        status, _, payload = handle_register(body)
        assert status == 400
        assert b"cross_verification_failed" in payload




def test_non_strict_mode_allows_bad_cross_verify(temp_registry_store):
    entry = _signed()
    with patch("api._handlers.register.cross_verify",
               return_value={"ok": False, "reason": "score mismatch"}):
        body = json.dumps({"entry": entry, "strict": False})
        status, _, _payload = handle_register(body)
        assert status == 200
