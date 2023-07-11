"""Test conf/user.py."""
from pathlib import Path

from mse_cli.cloud.model.user import UserConf


def test_load():
    """Test `load` function."""
    toml = Path(__file__).parent / "data/user.toml"
    conf = UserConf.load(path=toml)

    ref_user_conf = UserConf(email="john@example.com", refresh_token="my_token")

    assert conf == ref_user_conf
