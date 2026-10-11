# NTI Registry


**Federated, cryptographically signed directory of every NTI-1 certified tool.**


[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


## Why This Is Different


Existing registries (PyPI, npm, awesome-lists) let anyone claim anything. This registry requires **cryptographic proof of compliance**:


- Every entry is **Dilithium5-signed** by the tool owner
- Every entry is **cross-verified against a live nti-badge node**
- Every entry is **machine-readable** for AI agent discovery
- Every entry is **offline-verifiable** forever
- The registry is **federated** — anyone can mirror it


No central authority. No silent edits. No self-claimed trust.


## Endpoints


- POST /api/register — submit a signed entry
- GET  /api/list — full list of entries
- GET  /api/verify?id=... — verify one entry
- GET  /api/search?q=...&category=... — filter entries
- GET  /api/federation — federation manifest
- POST /api/federation/register — register a peer registry
- GET  /api/sync?from=... — pull entries from a peer
- GET  /api/stats — public counters
- GET  /api/health — health check


## License


Apache License 2.0. See LICENSE.


## Links


- NTI-1 Spec: https://abisheakp197.github.io/nti-spec/
- nti-scanner: https://pypi.org/project/nti-scanner/
- nti-badge: https://nti-badge-svs1.vercel.app
- nti-attack: https://pypi.org/project/nti-attack/
- nti-benchmark: https://pypi.org/project/nti-benchmark/
