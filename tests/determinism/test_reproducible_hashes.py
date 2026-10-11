"""Same input = same hash. Always."""


from lib.signing import compute_cert_hash
from lib.entries import build_entry




def test_same_entry_same_hash():
    e = build_entry(
        name="x", version="0.1.0", description="d", category="framework",
        repo_url="https://x", badge_url="https://y", nti_score=90,
    )
    # Remove id and registered_at for deterministic test
    e.pop("id", None)
    e.pop("registered_at", None)
    h1 = compute_cert_hash(e)
    h2 = compute_cert_hash(e)
    assert h1 == h2




def test_key_order_does_not_matter():
    e1 = {"a": 1, "b": 2}
    e2 = {"b": 2, "a": 1}
    assert compute_cert_hash(e1) == compute_cert_hash(e2)




def test_different_values_different_hash():
    e1 = {"a": 1}
    e2 = {"a": 2}
    assert compute_cert_hash(e1) != compute_cert_hash(e2)
