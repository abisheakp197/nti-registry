"""Tamper detection across every field."""


from lib.entries import build_entry
from lib.signing import sign_payload, verify_integrity


def _fresh_signed():
    e = build_entry(
        name="x", version="0.1.0", description="d", category="framework",
        repo_url="https://github.com/a/b", badge_url="https://y.com", nti_score=90,
    )
    return sign_payload(e)




def test_tamper_name():
    s = _fresh_signed()
    s["name"] = "evil"
    assert verify_integrity(s) is False




def test_tamper_score():
    s = _fresh_signed()
    s["nti_score"] = 100
    assert verify_integrity(s) is False




def test_tamper_repo():
    s = _fresh_signed()
    s["repo_url"] = "https://evil.com/x"
    assert verify_integrity(s) is False




def test_tamper_cert_hash():
    s = _fresh_signed()
    s["cert_hash"] = "0" * 64
    assert verify_integrity(s) is False




def test_tamper_pubkey():
    s = _fresh_signed()
    s["issuer_pubkey"] = "ff" * 100
    assert verify_integrity(s) is False
