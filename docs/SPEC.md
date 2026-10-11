# NTI-Registry/1 Specification


**Version:** 1.0
**Status:** Draft
**License:** Apache 2.0


## Purpose


A federated, cryptographically signed directory of every NTI-1 certified AI agent tool.


## Design Principles


1. **Signed** — every entry is Dilithium5-signed by its owner
2. **Cross-verified** — entries are checked against a live nti-badge node
3. **Federated** — any org can run a mirror; nodes sync peer-to-peer
4. **Offline-verifiable** — anyone can verify an entry without network
5. **Append-only history** — entries are immutable; updates create new entries
6. **Machine-readable** — JSON for AI agent discovery
7. **No vendor lock-in** — anyone can deploy their own registry


## Entry Format


See `web/docs.html` for the full example.


## Verification Algorithm


1. Parse JSON entry
2. Remove `signature` and `cert_hash`
3. Serialize canonically (sort_keys=True)
4. Compute SHA-256 → compare to `cert_hash`
5. Confirm `signature` and `issuer_pubkey` are present
6. (When the API supports it) verify Dilithium5 signature using `issuer_pubkey`


## Federation Protocol


A registry node MUST expose at minimum:
- GET /api/list
- GET /api/verify
- GET /api/federation
- POST /api/federation/register
- GET /api/sync


A registry node MUST NOT:
- Modify entries (append-only)
- Require registration to read
- Have exclusive control over the format


## Neutrality


Registry operators forward signed data. They do not vouch. If they act in bad faith, entries remain valid because they are signed by their owners and verifiable offline.
