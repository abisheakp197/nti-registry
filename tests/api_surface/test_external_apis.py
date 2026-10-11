"""Real external API checks. Must run first. No mocks."""




def test_pqc_key_pair_real():
    from ube_foundation import PqcKeyPair
    key = PqcKeyPair()
    assert key is not None
    pubkey = key.public_key_hex()
    assert isinstance(pubkey, str)
    assert len(pubkey) > 100




def test_pqc_sign_returns_hex_string():
    from ube_foundation import PqcKeyPair
    key = PqcKeyPair()
    sig = key.sign(b"hello")
    assert isinstance(sig, str)
    assert len(sig) > 100




def test_pqc_sign_verify_roundtrip():
    from ube_foundation import PqcKeyPair
    key = PqcKeyPair()
    msg = b"roundtrip test"
    sig = key.sign(msg)
    assert key.verify(msg, sig) is True




def test_pqc_verify_rejects_tampered():
    from ube_foundation import PqcKeyPair
    key = PqcKeyPair()
    sig = key.sign(b"original")
    assert key.verify(b"tampered", sig) is False
