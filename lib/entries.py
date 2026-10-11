"""Registry entry model. Every entry is signed, cross-verified, and portable."""


import json
import uuid
from datetime import datetime, timezone
from typing import Optional




CATEGORIES = {
    "framework",     # LangChain, CrewAI, AutoGen, MAF
    "scanner",       # nti-scanner
    "badge",         # nti-badge
    "attack",        # nti-attack
    "benchmark",     # nti-benchmark
    "template",      # nti-agent-template
    "spec",          # nti-spec
    "sdk",           # ube-foundation
    "other",
}


PILLARS = {"Identity", "Governance", "Consensus", "Audit", "Persistence"}




def build_entry(
    name: str,
    version: str,
    description: str,
    category: str,
    repo_url: str,
    badge_url: str,
    nti_score: int,
    owner_contact: str = "",
    docs_url: str = "",
) -> dict:
    """Build a registry entry. Unsigned. Call sign_payload() to sign."""
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Must be one of {CATEGORIES}")
    if not (0 <= nti_score <= 100):
        raise ValueError("nti_score must be 0-100")


    return {
        "spec": "NTI-Registry-Entry/1",
        "id": str(uuid.uuid4()),
        "name": name,
        "version": version,
        "description": description[:500],
        "category": category,
        "repo_url": repo_url,
        "badge_url": badge_url,
        "docs_url": docs_url,
        "nti_score": int(nti_score),
        "owner_contact": owner_contact,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }




def validate_entry(entry: dict) -> None:
    """Raise if entry is malformed."""
    required = ["spec", "id", "name", "version", "category", "repo_url",
                "badge_url", "nti_score", "registered_at"]
    for f in required:
        if f not in entry:
            raise ValueError(f"Missing required field: {f}")
    if entry["spec"] != "NTI-Registry-Entry/1":
        raise ValueError(f"Wrong spec: {entry['spec']}")
    if entry["category"] not in CATEGORIES:
        raise ValueError(f"Invalid category: {entry['category']}")
    if not isinstance(entry["nti_score"], int) or not (0 <= entry["nti_score"] <= 100):
        raise ValueError(f"Invalid nti_score: {entry['nti_score']}")
