"""Entry builder and validator."""


import pytest
from lib.entries import build_entry, validate_entry, CATEGORIES




def test_build_entry_minimum():
    e = build_entry(
        name="x", version="0.1.0", description="desc", category="framework",
        repo_url="https://github.com/a/b", badge_url="https://x.com", nti_score=90,
    )
    assert e["spec"] == "NTI-Registry-Entry/1"
    assert e["name"] == "x"
    assert e["nti_score"] == 90
    assert "id" in e
    assert "registered_at" in e




def test_build_entry_invalid_category():
    with pytest.raises(ValueError):
        build_entry(
            name="x", version="0.1.0", description="d", category="garbage",
            repo_url="https://x", badge_url="https://y", nti_score=50,
        )




def test_build_entry_invalid_score_high():
    with pytest.raises(ValueError):
        build_entry(
            name="x", version="0.1.0", description="d", category="framework",
            repo_url="https://x", badge_url="https://y", nti_score=101,
        )




def test_build_entry_invalid_score_low():
    with pytest.raises(ValueError):
        build_entry(
            name="x", version="0.1.0", description="d", category="framework",
            repo_url="https://x", badge_url="https://y", nti_score=-1,
        )




def test_validate_entry_full(sample_entry_raw):
    validate_entry(sample_entry_raw)




def test_validate_entry_missing_field(sample_entry_raw):
    bad = dict(sample_entry_raw)
    del bad["name"]
    with pytest.raises(ValueError):
        validate_entry(bad)




def test_validate_entry_wrong_spec(sample_entry_raw):
    bad = dict(sample_entry_raw)
    bad["spec"] = "NTI-Registry-Entry/2"
    with pytest.raises(ValueError):
        validate_entry(bad)




def test_all_categories_are_valid():
    for cat in CATEGORIES:
        build_entry(
            name="x", version="0.1.0", description="d", category=cat,
            repo_url="https://x", badge_url="https://y", nti_score=50,
        )
