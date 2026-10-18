"""Cold start: all modules import cleanly."""


def test_all_modules_import():
    import api
    import api._handlers
    import api.index
    import lib
    import lib.attestation
    import lib.db
    import lib.entries
    import lib.federation_client
    import lib.signing
    import lib.verifier
    assert lib is not None
    assert api is not None
