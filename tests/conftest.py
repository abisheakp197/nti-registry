"""Shared fixtures."""


import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))




@pytest.fixture
def sample_entry_raw():
    return {
        "spec": "NTI-Registry-Entry/1",
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "test-tool",
        "version": "0.1.0",
        "description": "A test tool for verification",
        "category": "framework",
        "repo_url": "https://github.com/abisheakp197/langchain-nti",
        "badge_url": "https://nti-badge-svs1.vercel.app",
        "docs_url": "",
        "nti_score": 95,
        "owner_contact": "test@example.com",
        "registered_at": "2026-01-15T10:00:00+00:00",
    }




@pytest.fixture
def temp_registry_store(tmp_path, monkeypatch):
    monkeypatch.setenv("NTI_LOCAL_STORE", str(tmp_path / "registry-data"))
    import importlib

    import lib.db
    importlib.reload(lib.db)
    yield tmp_path / "registry-data"
