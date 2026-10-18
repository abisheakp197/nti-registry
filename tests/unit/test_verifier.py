"""Verifier helpers."""


from lib.verifier import _repo_from_url


def test_repo_from_url_github():
    assert _repo_from_url("https://github.com/owner/repo") == "owner/repo"




def test_repo_from_url_git_suffix():
    assert _repo_from_url("https://github.com/owner/repo.git") == "owner/repo"




def test_repo_from_url_trailing_slash():
    assert _repo_from_url("https://github.com/owner/repo/") == "owner/repo"




def test_repo_from_url_invalid():
    assert _repo_from_url("") == ""
