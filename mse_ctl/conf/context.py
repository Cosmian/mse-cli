"""Context file."""

import os
import tempfile
from pathlib import Path
from uuid import UUID

import toml
from pydantic import BaseModel, validator

from mse_ctl import MSE_CONF_DIR
from mse_ctl.conf.app import AppConf
from mse_ctl.utils.crypto import random_symkey


class Context(BaseModel):
    """Definition of a mse context."""

    # Name of the mse instance
    name: str
    # Version of the mse instance
    version: str
    # Project parent of the app
    project: str
    # Unique id of the service enclave
    id: UUID
    # Domain name of the service
    domain_name: str
    # Temporary file save
    workspace: Path
    # Symetric used to encrypt the code
    symkey: bytes

    @validator('symkey', pre=True, always=True)
    def set_symkey(cls, v, values, **kwargs):
        """Set symkey from a value for pydantic."""
        return bytes.fromhex(v) if isinstance(v, str) else v

    @property
    def encrypted_code_path(self):
        """Get the path to store the encrypted code."""
        return self.workspace / "encrypted_code"

    @property
    def tar_code_path(self):
        """Get the path to store the tar code."""
        return self.workspace / "code.tar"

    @property
    def path(self) -> Path:
        """Get the path of the node context."""
        return MSE_CONF_DIR / "contexts" / (str(self.id) + ".mse")

    @staticmethod
    def from_app_conf(conf: AppConf):
        """Build a Context object from an app conf."""
        workspace = Path(tempfile.gettempdir()) / conf.service_identifier

        dataMap = {
            "name": conf.name,
            "version": conf.version,
            "project": conf.project,
            "id": "00000000-0000-0000-0000-000000000000",
            "domain_name": "",
            "workspace": workspace,
            "symkey": bytes(random_symkey()).hex()
        }

        os.makedirs(workspace, exist_ok=True)

        return Context(**dataMap)

    @staticmethod
    def from_toml(path: Path):
        """Build a Context object from a Toml file."""
        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

            return Context(**dataMap)

    def save(self):
        """Dump the current object to a file."""
        # TODO: put symkey in hex
        os.makedirs(self.path.parent, exist_ok=True)

        with open(self.path, "w", encoding="utf8") as f:
            dataMap = {
                "name": self.name,
                "version": self.version,
                "project": self.project,
                "id": str(self.id),
                "domain_name": self.domain_name,
                "workspace": str(self.workspace),
                "symkey": bytes(self.symkey).hex()
            }
            toml.dump(dataMap, f)
