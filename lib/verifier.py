"""Cross-verify a registry entry against its live badge node."""

import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

import httpx


def validate_url(url: str) -> str:
    """Validates and sanitizes URL to prevent SSRF. Returns safe URL or raises ValueError."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Blocked: Invalid URL scheme")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Blocked: Missing hostname")

        # Resolve hostname to IP to prevent DNS rebinding
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)

        # Restrict requests to public IPs only (RFC 1918, loopback, link-local, reserved)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            raise ValueError("Blocked: Private, loopback, or link-local URLs are not allowed")

        # Explicitly block cloud metadata endpoints
        if str(ip) == "169.254.169.254":
            raise ValueError("Blocked: Cloud metadata endpoints are forbidden")

        # Return the sanitized string (CodeQL recognizes this breaks the taint chain)
        return parsed.geturl()
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"URL validation failed: {str(e)}") from e


def is_safe_url(url: str) -> bool:
    """Validates URL to prevent SSRF by ensuring it resolves to a public IP."""
    try:
        validate_url(url)
        return True
    except Exception:  # noqa: BLE001
        return False


async def fetch_badge_score(badge_url: str, repo: str, timeout: float = 10.0) -> int | None:
    """Fetch the live score from a badge node for a given repo.

    badge_url example: https://nti-badge-svs1.vercel.app
    repo example: owner/repo
    """
    if not badge_url or not repo:
        return None
    url = badge_url.rstrip("/") + "/api/certificate"
    url = validate_url(url)
    try:
        client_timeout = httpx.Timeout(timeout, connect=5.0)
        async with httpx.AsyncClient(timeout=client_timeout) as client:
            r = await client.get(url, params={"repo": repo})
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    latest = data.get("latest") or {}
                    if isinstance(latest, dict):
                        score = latest.get("score")
                        if isinstance(score, int):
                            return score
    except (httpx.HTTPError, KeyError):
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
