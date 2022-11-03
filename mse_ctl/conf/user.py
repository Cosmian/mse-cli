"""User configuration file module."""

from pathlib import Path

import toml
from pydantic import BaseModel

from mse_ctl import MSE_BACKEND_URL, MSE_CONF_DIR
from mse_ctl.api.auth import Connection


class UserConf(BaseModel):
    """Definition of the user param."""

    # Email of the user
    email: str
    # Secret token of the user
    secret_token: str

    @staticmethod
    def path() -> Path:
        """Get the path of the user conf."""
        return MSE_CONF_DIR / "login.toml"

    @staticmethod
    def from_toml():
        """Build a UserConf object from a Toml file."""
        with open(UserConf.path(), encoding="utf8") as f:
            dataMap = toml.load(f)

            return UserConf(**dataMap)

    def get_connection(self) -> Connection:
        """Get the connection to the backend."""
        return Connection(base_url=MSE_BACKEND_URL,
                          refresh_token=self.secret_token)
