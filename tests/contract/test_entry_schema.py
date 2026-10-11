"""Every entry must satisfy the spec."""


import json
import pytest
from lib.entries import build_entry
from lib.signing import sign_payload, verify_integrity, verify_signature




REQUIRED_FIELDS = [
    "spec", "id", "name", "version", "description", "category",
    "repo_url", "badge_url", "nti_score", "registered_at",
    "issuer_pubkey", "signature", "cert_hash",
]




def test_signed_entry_has_all_required_fields(sample_entry_raw):
    signed = sign_payload(sample_entry_raw)
    for f in REQUIRED_FIELDS:
        assert f in signed, f"Missing field: {f}"




def test_signed_entry_json_serializable(sample_entry_raw):
    signed = sign_payload(sample_entry_raw)
    raw = json.dumps(signed)
    assert isinstance(raw, str)
    assert len(raw) > 0




def test_entry_roundtrip(sample_entry_raw):
    signed = sign_payload(sample_entry_raw)
    raw = json.dumps(signed)
    parsed = json.loads(raw)
    assert verify_integrity(parsed) is True
    assert verify_signature(parsed) is True
