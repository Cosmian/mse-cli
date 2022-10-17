"""User configuration file module."""

from enum import Enum
import toml
from pathlib import Path
import os
from pydantic import BaseModel
from mse_ctl.api.auth import Connection


class UserConf(BaseModel):
    """Definition of an enclave by a user."""

    # Email of the user
    email: str
    # Access token of the user
    secret_token: str

    @staticmethod
    def path() -> str:
        """Get the path of the user conf."""
        return os.getenv('MSE_CTL_USER_CONF', "mse.toml")

    @staticmethod
    def from_toml():
        """Build a UserConf object from a Toml file."""
        with open(UserConf.path()) as f:
            dataMap = toml.load(f)

            return UserConf(**dataMap)

    def get_connection(self):
        """Get the connection to the backend."""
        return Connection(base_url=os.getenv(
            'MSE_CTL_BASE_URL', default="https://backend.mse.cosmian.com"),
                          refresh_token=self.secret_token)
