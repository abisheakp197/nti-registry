"""Cross-verify a registry entry against its live badge node."""

from typing import Any

import httpx


async def fetch_badge_score(badge_url: str, repo: str, timeout: float = 10.0) -> int | None:
    """Fetch the live score from a badge node for a given repo.

    badge_url example: https://nti-badge-svs1.vercel.app
    repo example: owner/repo
    """
    if not badge_url or not repo:
        return None
    url = badge_url.rstrip("/") + "/api/certificate"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params={"repo": repo})
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    latest = data.get("latest") or {}
                    if isinstance(latest, dict):
                        score = latest.get("score")
                        if isinstance(score, int):
                            return score
    except (httpx.HTTPError, ValueError, KeyError):
        return None
    return None


async def cross_verify(entry: dict[str, Any]) -> dict[str, Any]:
    """Check if the entry's claimed score matches its live badge node."""
    badge_url = str(entry.get("badge_url", ""))
    repo_url = str(entry.get("repo_url", ""))
    claimed_score = entry.get("nti_score")

    live_score = await fetch_badge_score(badge_url, _repo_from_url(repo_url))
    if live_score is None:
        return {"ok": False, "reason": "badge node unreachable", "live_score": None}
    if live_score != claimed_score:
        return {"ok": False, "reason": "score mismatch", "live_score": live_score, "claimed": claimed_score}
    return {"ok": True, "live_score": live_score}


def _repo_from_url(repo_url: str) -> str:
    """Extract owner/repo from https://github.com/owner/repo."""
    url = repo_url.rstrip("/").replace(".git", "")
    parts = url.split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return ""
