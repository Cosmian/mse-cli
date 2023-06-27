"""Test boostrap.py."""

from uuid import UUID

from mse_cli.core.bootstrap import ConfigurationPayload


def test_payload():
    """Test `payload` function."""
    conf = ConfigurationPayload(
        app_id=UUID("63322f85-1ff8-4483-91ae-f18d7398d157"),
        secrets=None,
        sealed_secrets=None,
        code_secret_key=None,
    )

    assert conf.payload() == {
        "uuid": "63322f85-1ff8-4483-91ae-f18d7398d157",
    }

    conf = ConfigurationPayload(
        app_id=UUID("63322f85-1ff8-4483-91ae-f18d7398d157"),
        secrets={"key": "password"},
        sealed_secrets=b"123456789",
        code_secret_key=b"abcdefg",
    )

    assert conf.payload() == {
        "uuid": "63322f85-1ff8-4483-91ae-f18d7398d157",
        "app_secrets": {"key": "password"},
        "app_sealed_secrets": "MTIzNDU2Nzg5",
        "code_secret_key": "61626364656667",
    }
