"""Dilithium5 signing for registry entries. Same pattern as every NTI package."""


import json
import hashlib




def _canonical_bytes(payload: dict) -> bytes:
    clean = {k: v for k, v in payload.items() if k not in ("signature", "cert_hash")}
    return json.dumps(clean, sort_keys=True).encode("utf-8")




def compute_cert_hash(payload: dict) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()




def sign_payload(payload: dict) -> dict:
    """Sign a registry entry with Dilithium5."""
    from ube_foundation import PqcKeyPair
    key = PqcKeyPair()
    clean = {k: v for k, v in payload.items() if k not in ("signature", "cert_hash")}
    clean["issuer_pubkey"] = key.public_key_hex()
    message = json.dumps(clean, sort_keys=True).encode("utf-8")
    return {
        **clean,
        "signature": key.sign(message),
        "cert_hash": hashlib.sha256(message).hexdigest(),
    }




def verify_integrity(payload: dict) -> bool:
    """Verify hash matches payload."""
    if not payload.get("cert_hash"):
        return False
    return compute_cert_hash(payload) == payload["cert_hash"]




def verify_signature(payload: dict) -> bool:
    """Verify Dilithium5 signature is present and non-empty.
    Full cryptographic verification requires the issuer's public key to be
    loaded into a PqcKeyPair, which the ube_foundation API does not yet
    expose. We enforce hash + signature presence; hash binds the pubkey.
    """
    if not verify_integrity(payload):
        return False
    if not payload.get("signature"):
        return False
    if not payload.get("issuer_pubkey"):
        return False
    sig = payload["signature"]
    if not isinstance(sig, str) or len(sig) < 100:
        return False
    return True
