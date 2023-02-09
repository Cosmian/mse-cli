"""mse_cli.conf.user module."""

from pathlib import Path
from typing import Dict, Optional

import toml
from pydantic import BaseModel

from mse_cli import (
    MSE_AUTH0_CLIENT_ID,
    MSE_AUTH0_DOMAIN_NAME,
    MSE_BACKEND_URL,
    MSE_CONF_DIR,
)
from mse_cli.api.auth import Connection


class UserConf(BaseModel):
    """Definition of the user param."""

    # Email of the user
    email: str
    # Refresh token of the user
    refresh_token: str

    @staticmethod
    def path() -> Path:
        """Get the path of the user conf."""
        return MSE_CONF_DIR / "login.toml"

    @staticmethod
    def from_toml(path: Optional[Path] = None):
        """Build a UserConf object from a Toml file."""
        if not path:
            path = UserConf.path()

        if not path.exists():
            raise FileNotFoundError("You shall login before proceed")

        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

            return UserConf(**dataMap)

    def save(self, path: Optional[Path] = None):
        """Dump the current object to a file."""
        if not path:
            path = UserConf.path()

        with open(path, "w", encoding="utf8") as f:
            dataMap: Dict[str, str] = {
                "email": self.email,
                "refresh_token": self.refresh_token,
            }

            toml.dump(dataMap, f)

    def get_connection(self) -> Connection:
        """Get the connection to the backend."""
        return Connection(
            base_url=MSE_BACKEND_URL,
            auth0_base_url=MSE_AUTH0_DOMAIN_NAME,
            client_id=MSE_AUTH0_CLIENT_ID,
            refresh_token=self.refresh_token,
        )
