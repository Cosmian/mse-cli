"""Context file."""

import os
import tempfile
from pathlib import Path
from uuid import UUID

import toml
from pydantic import BaseModel, validator

from mse_ctl import MSE_CONF_DIR
from mse_ctl.conf.app import AppConf, CodeProtection, EnclaveSize
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
    # Symetric used to encrypt the code
    symkey: bytes
    # Wether the code is encrypted or not
    code_protection: CodeProtection
    # Size of the enclave
    enclave_size: EnclaveSize
    # Lifetime of the spawned enclave
    enclave_lifetime: int
    # from python_flask_module import python_flask_variable_name
    python_application: str
    # The mse-docker version
    docker_version: str

    @validator('symkey', pre=True, always=True)
    def set_symkey(cls, v, values, **kwargs):
        """Set symkey from a value for pydantic."""
        return bytes.fromhex(v) if isinstance(v, str) else v

    @property
    def docker_log_path(self):
        """Get the path to store the docker logs."""
        return self.workspace / "docker.log"

    @property
    def cert_path(self):
        """Get the path to store the certificate."""
        return self.workspace / "cert.pem"

    @property
    def decrypted_code_path(self):
        """Get the path to store the decrypted code."""
        path = self.workspace / "decrypted_code"
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def encrypted_code_path(self):
        """Get the path to store the encrypted code."""
        path = self.workspace / "encrypted_code"
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def tar_code_path(self):
        """Get the path to store the tar code."""
        return self.workspace / "code.tar"

    @property
    def exported_path(self) -> Path:
        """Get the path of the context."""
        path = MSE_CONF_DIR / "context"
        os.makedirs(path, exist_ok=True)
        return path / (str(self.id) + ".mse")

    @property
    def workspace(self) -> Path:
        path = Path(tempfile.gettempdir()) / f"{self.name}-{self.version}"
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def from_app_conf(conf: AppConf):
        """Build a Context object from an app conf."""
        dataMap = {
            "name": conf.name,
            "version": conf.version,
            "project": conf.project,
            "id": "00000000-0000-0000-0000-000000000000",
            "domain_name": "",
            "code_protection": conf.code_protection,
            "enclave_size": conf.enclave_size,
            "enclave_lifetime": conf.enclave_lifetime,
            "python_application": conf.python_application,
            "symkey": bytes(random_symkey()).hex(),
            "docker_version": ""
        }

        return Context(**dataMap)

    @staticmethod
    def from_toml(path: Path):
        """Build a Context object from a Toml file."""
        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

        return Context(**dataMap)

    def run(self, uuid: UUID, domain_name: str, docker_version: str):
        """Complete the context since the app is now running."""
        self.id = uuid
        self.domain_name = domain_name
        self.docker_version = docker_version

    def save(self):
        """Dump the current object to a file."""
        with open(self.exported_path, "w", encoding="utf8") as f:
            dataMap = {
                "name": self.name,
                "version": self.version,
                "project": self.project,
                "id": str(self.id),
                "domain_name": self.domain_name,
                "symkey": bytes(self.symkey).hex(),
                "code_protection": self.code_protection.value,
                "enclave_size": self.enclave_size.value,
                "enclave_lifetime": self.enclave_lifetime,
                "python_application": self.python_application,
                "docker_version": self.docker_version
            }
            toml.dump(dataMap, f)
