"""Dilithium5 signing for registry entries. Same pattern as every NTI package."""

import hashlib
import json
from typing import Any


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    clean = {k: v for k, v in payload.items() if k not in ("signature", "cert_hash")}
    return json.dumps(clean, sort_keys=True).encode("utf-8")


def compute_cert_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def sign_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Sign a registry entry with Dilithium5."""
    from ube_foundation import PqcKeyPair  # type: ignore[import-untyped]

    key = PqcKeyPair()
    clean = {k: v for k, v in payload.items() if k not in ("signature", "cert_hash")}
    clean["issuer_pubkey"] = key.public_key_hex()
    message = json.dumps(clean, sort_keys=True).encode("utf-8")
    return {
        **clean,
        "signature": key.sign(message),
        "cert_hash": hashlib.sha256(message).hexdigest(),
    }


def verify_integrity(payload: dict[str, Any]) -> bool:
    """Verify hash matches payload."""
    if not payload.get("cert_hash"):
        return False
    return bool(compute_cert_hash(payload) == payload["cert_hash"])


def verify_signature(payload: dict[str, Any]) -> bool:
    """Verify Dilithium5 signature presence, issuer pubkey, and payload hash integrity."""
    if not verify_integrity(payload):
        return False
    if not payload.get("signature"):
        return False
    if not payload.get("issuer_pubkey"):
        return False
    sig = payload["signature"]
    if not isinstance(sig, str) or len(sig) < 100:
        return False
    pubkey = payload["issuer_pubkey"]
    return isinstance(pubkey, str) and len(pubkey) >= 16
