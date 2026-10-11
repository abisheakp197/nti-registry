# Submitting to the NTI Registry


## Prerequisites


Your tool must:
1. Have a live nti-badge node returning a score
2. Have a public repo URL
3. Have a version number


## How To Submit


Use the ube-foundation SDK to sign an entry:


from ube_foundation import PqcKeyPair
from lib.entries import build_entry
from lib.signing import sign_payload


entry = build_entry(
    name="your-tool",
    version="0.1.0",
    description="What your tool does",
    category="framework",
    repo_url="https://github.com/you/your-tool",
    badge_url="https://your-badge-node.com",
    nti_score=95,
    owner_contact="you@example.com",
)
signed = sign_payload(entry)


Then POST:


curl -X POST https://nti-registry.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{"entry": <signed>, "strict": true}'


## Rejection Reasons


- Missing required fields
- Hash mismatch
- Signature missing
- Cross-verification failed (badge node score does not match claimed score)
- Invalid category


## Cross-Verification


The registry contacts your badge node at `<badge_url>/api/certificate?repo=owner/repo`.
Your claimed score must match the live score from your badge node.


If you have no badge node, run one:
https://github.com/abisheakp197/nti-badge
