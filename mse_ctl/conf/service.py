"""Enclave configuration file module."""

from enum import Enum
import tempfile
from uuid import UUID
import toml
import os
from pathlib import Path

from pydantic import BaseModel

from mse_ctl.conf.enclave import EnclaveConf
from mse_ctl.utils.crypto import random_symkey
from mse_ctl import MSE_CONF_DIR


class Service(BaseModel):
    """Definition of a mse context."""

    # Name of the mse instance
    name: str
    # Version of the mse instance
    version: str
    # Unique id of the service enclave
    id: UUID
    # Domain name of the service
    domain_name: str
    # Temporary file save
    workspace: Path
    # Symetric used to encrypt the code
    symkey: bytes

    @property
    def encrypted_code_path(self):
        return self.workspace / "encrypted_code"

    @property
    def tar_code_path(self):
        return self.workspace / "code.tar"

    @property
    def path(self) -> str:
        """Get the path of the service context."""
        return MSE_CONF_DIR / "services" / (str(self.id) + ".mse")

    @staticmethod
    def from_enclave_conf(conf: EnclaveConf):
        """Build a Service object from an enclave conf."""
        workspace = Path(tempfile.gettempdir()) / conf.service_identifier

        dataMap = {
            "name": conf.service_name,
            "version": conf.service_version,
            "id": "00000000-0000-0000-0000-000000000000",
            "domain_name": "",
            "workspace": workspace,
            "symkey": random_symkey()
        }

        os.makedirs(workspace, exist_ok=True)

        return Service(**dataMap)

    @staticmethod
    def from_toml(path: Path):
        """Build a Service object from a Toml file."""
        with open(path) as f:
            dataMap = toml.load(f)

            return Service(**dataMap)

    def save(self):
        """Dump the current object to a file."""
        os.makedirs(self.path.parent, exist_ok=True)

        with open(self.path, "w") as f:
            dataMap = {
                "name": self.name,
                "version": self.version,
                "id": str(self.id),
                "domain_name": self.domain_name,
                "workspace": str(self.workspace),
                "symkey": self.symkey
            }
            toml.dump(dataMap, f)
