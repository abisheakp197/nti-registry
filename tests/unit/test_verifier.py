"""Verifier helpers and security tests."""

import asyncio
import pytest

from lib.verifier import _repo_from_url, cross_verify, fetch_badge_score, validate_url


def test_repo_from_url_github():
    assert _repo_from_url("https://github.com/owner/repo") == "owner/repo"


def test_repo_from_url_git_suffix():
    assert _repo_from_url("https://github.com/owner/repo.git") == "owner/repo"


def test_repo_from_url_trailing_slash():
    assert _repo_from_url("https://github.com/owner/repo/") == "owner/repo"


def test_repo_from_url_invalid():
    assert _repo_from_url("") == ""


def test_ssrf_blocked_loopback_and_metadata():
    with pytest.raises(ValueError):
        asyncio.run(fetch_badge_score("http://127.0.0.1", "owner/repo"))

    with pytest.raises(ValueError):
        asyncio.run(fetch_badge_score("http://169.254.169.254", "owner/repo"))

    with pytest.raises(ValueError):
        validate_url("http://127.0.0.1")

    with pytest.raises(ValueError):
        validate_url("http://169.254.169.254")

    with pytest.raises(ValueError):
        asyncio.run(cross_verify({"badge_url": "http://127.0.0.1", "repo_url": "https://github.com/owner/repo"}))
