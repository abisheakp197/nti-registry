"""Tests for cryptographic signature verification and fail-closed security rules."""

import json
from unittest.mock import patch

from api._handlers.register import handle_register
from api.index import route
from lib.entries import build_entry
from lib.signing import sign_payload, verify_signature


def test_verify_signature_detects_missing_fields():
    entry = build_entry(
        name="test",
        version="1.0.0",
        description="desc",
        category="framework",
        repo_url="https://github.com/org/repo",
        badge_url="https://badge.example.com",
        nti_score=95,
    )
    signed = sign_payload(entry)

    # Valid signed entry
    assert verify_signature(signed) is True

    # Missing signature
    no_sig = dict(signed)
    no_sig.pop("signature")
    assert verify_signature(no_sig) is False

    # Missing issuer pubkey
    no_key = dict(signed)
    no_key.pop("issuer_pubkey")
    assert verify_signature(no_key) is False

    # Corrupted signature
    bad_sig = dict(signed)
    bad_sig["signature"] = "short"
    assert verify_signature(bad_sig) is False


def test_register_rejects_missing_signature(temp_registry_store):
    entry = build_entry(
        name="test",
        version="1.0.0",
        description="desc",
        category="framework",
        repo_url="https://github.com/org/repo",
        badge_url="https://badge.example.com",
        nti_score=95,
    )
    # Entry missing signature & hash
    body = json.dumps({"entry": entry, "strict": False})
    status, _, payload = handle_register(body)
    assert status == 400
    assert b"hash_mismatch" in payload or b"invalid_signature" in payload


def test_register_rejects_corrupted_signature(temp_registry_store):
    entry = build_entry(
        name="test",
        version="1.0.0",
        description="desc",
        category="framework",
        repo_url="https://github.com/org/repo",
        badge_url="https://badge.example.com",
        nti_score=95,
    )
    signed = sign_payload(entry)
    signed["signature"] = "invalid_sig_string"
    body = json.dumps({"entry": signed, "strict": False})

    with patch("api._handlers.register.cross_verify", return_value={"ok": True}):
        status, _, payload = handle_register(body)
        assert status == 400
        assert b"invalid_signature" in payload


def test_oversized_payload_rejected(temp_registry_store):
    large_payload = "a" * (1024 * 1024 + 100)  # > 1MB
    status, _, payload = route("POST", "/api/register", {}, large_payload)
    assert status == 413
    assert b"payload_too_large" in payload
