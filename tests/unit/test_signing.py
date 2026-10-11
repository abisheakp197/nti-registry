"""Signing and verification."""


from lib.signing import compute_cert_hash, sign_payload, verify_integrity, verify_signature




def test_hash_is_deterministic(sample_entry_raw):
    h1 = compute_cert_hash(sample_entry_raw)
    h2 = compute_cert_hash(sample_entry_raw)
    assert h1 == h2
    assert len(h1) == 64




def test_sign_and_verify(sample_entry_raw):
    signed = sign_payload(sample_entry_raw)
    assert "signature" in signed
    assert "cert_hash" in signed
    assert "issuer_pubkey" in signed
    assert verify_integrity(signed) is True
    assert verify_signature(signed) is True




def test_tamper_detected(sample_entry_raw):
    signed = sign_payload(sample_entry_raw)
    signed["nti_score"] = 0
    assert verify_integrity(signed) is False
    assert verify_signature(signed) is False




def test_missing_signature_fails(sample_entry_raw):
    signed = sign_payload(sample_entry_raw)
    del signed["signature"]
    assert verify_signature(signed) is False




def test_missing_cert_hash_fails(sample_entry_raw):
    signed = sign_payload(sample_entry_raw)
    del signed["cert_hash"]
    assert verify_integrity(signed) is False
