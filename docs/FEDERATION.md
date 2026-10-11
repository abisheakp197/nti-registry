# NTI Registry Federation


## Model


Any organization can run a registry node. Nodes announce themselves to peers. Nodes pull entries from peers. No central authority.


## How To Announce


POST to a peer's `/api/federation/register`:
{
  "url": "https://your-registry.example.com",
  "name": "your-org-registry",
  "kind": "registry"
}


## How To Sync From a Peer


GET /api/sync?from=https://peer.example.com


The node will:
1. Fetch the peer's full list
2. Verify each entry's hash integrity
3. Skip entries already present
4. Import new entries tagged with `imported_from` and `imported_at`


## Trust Model


Nodes do not trust each other. Every entry is signed by its owner. Nodes forward, never vouch. If an entry's hash fails, it is rejected on import.


## Why This Beats Centralization


- Central registries (PyPI, npm) can be shut down, change terms, or de-platform entries
- Federated registries cannot be shut down by any single actor
- The signature is the only authority — not the registry operator
