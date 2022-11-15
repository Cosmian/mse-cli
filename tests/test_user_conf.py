from pathlib import Path

from mse_ctl.conf.user import UserConf


def test_from_toml():
    """Test `from_toml` function."""
    toml = Path("tests/data/user.toml")
    conf = UserConf.from_toml(path=toml)

    ref_user_conf = UserConf(email="john@example.com", secret_token="my_token")

    assert conf == ref_user_conf
