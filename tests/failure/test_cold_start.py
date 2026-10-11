"""Cold start: all modules import cleanly."""


def test_all_modules_import():
    import lib
    import lib.db
    import lib.signing
    import lib.entries
    import lib.attestation
    import lib.verifier
    import lib.federation_client
    import api
    import api.index
    import api._handlers
    assert lib is not None
    assert api is not None
