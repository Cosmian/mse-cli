"""User configuration file module."""

import toml
import os

from pydantic import BaseModel
from mse_ctl.api.auth import Connection
from mse_ctl import MSE_CONF_DIR


class UserConf(BaseModel):
    """Definition of the user param."""

    # Email of the user
    email: str
    # Secret token of the user
    secret_token: str

    @staticmethod
    def path() -> str:
        """Get the path of the user conf."""
        return MSE_CONF_DIR / "login.toml"

    @staticmethod
    def from_toml():
        """Build a UserConf object from a Toml file."""
        with open(UserConf.path()) as f:
            dataMap = toml.load(f)

            return UserConf(**dataMap)

    def get_connection(self) -> Connection:
        """Get the connection to the backend."""
        return Connection(base_url=os.getenv(
            'MSE_CTL_BASE_URL', default="https://backend.mse.cosmian.com"),
                          refresh_token=self.secret_token)
