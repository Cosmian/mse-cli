"""Test base64.py."""

from mse_cli.core.base64 import base64url_decode, base64url_encode


def test_encode():
    """Test `base64url_encode`."""
    assert base64url_encode(b"") == ""
    assert base64url_encode(b"a") == "YQ"
    assert base64url_encode(b"ab") == "YWI"
    assert base64url_encode(b"abc") == "YWJj"
    assert base64url_encode(b"abcd") == "YWJjZA"
    assert base64url_encode(b"abcde") == "YWJjZGU"


def test_decode():
    """Test `base64url_decode`."""
    assert base64url_decode("") == b""
    assert base64url_decode("YQ") == b"a"
    assert base64url_decode("YWI") == b"ab"
    assert base64url_decode("YWJj") == b"abc"
    assert base64url_decode("YWJjZA") == b"abcd"
    assert base64url_decode("YWJjZGU") == b"abcde"
