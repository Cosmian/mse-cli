"""Context file."""

from enum import Enum
import os
import tempfile
from pathlib import Path
from uuid import UUID

import toml
from pydantic import BaseModel, validator

from mse_ctl import MSE_CONF_DIR
from mse_ctl.conf.app import AppConf
from mse_ctl.utils.crypto import random_symkey


class AppCertificateOrigin(str, Enum):
    """AppCertificateOrigin enum."""

    Self = "self"
    Owner = "owner"


class Context(BaseModel):
    """Definition of a mse context."""

    # Name of the mse instance
    name: str
    # Version of the mse instance
    version: str
    # Project parent of the app
    project: str
    # Unique id of the app
    id: UUID
    # Domain name of the app
    domain_name: str
    # Symetric used to encrypt the code
    symkey: bytes
    # Wether the code is encrypted or not
    encrypted_code: bool
    # Size of the enclave
    enclave_size: str
    # Lifetime of the spawned enclave
    expires_in: int
    # from python_flask_module import python_flask_variable_name
    python_application: str
    # The mse-docker version
    docker_version: str
    # The certificate of the app (self-signed or signed)
    ssl_app_certificate: str
    # Whether the certificate has been provided by the app owner
    app_certificate_origin: AppCertificateOrigin

    @validator('symkey', pre=True, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def set_symkey(cls, v, values, **kwargs):
        """Set symkey from a value for pydantic."""
        return bytes.fromhex(v) if isinstance(v, str) else v

    @property
    def docker_log_path(self):
        """Get the path to store the docker logs."""
        return self.workspace / "docker.log"

    @property
    def config_cert_path(self):
        """Get the path to store the certificate."""
        return self.workspace / "cert.conf.pem"

    @property
    def app_cert_path(self):
        """Get the path to store the certificate."""
        return self.workspace / "cert.app.pem"

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
        """Get the workspace path and create it."""
        path = Path(tempfile.gettempdir()) / f"{self.name}-{self.version}"
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def from_app_conf(conf: AppConf, enclave_size: int):
        """Build a Context object from an app conf."""
        return Context(name=conf.name,
                       version=conf.version,
                       project=conf.project,
                       id="00000000-0000-0000-0000-000000000000",
                       domain_name="",
                       encrypted_code=conf.code.encrypted,
                       enclave_size=enclave_size,
                       expires_in=0,
                       python_application=conf.code.python_application,
                       symkey=bytes(random_symkey()).hex(),
                       ssl_app_certificate="",
                       app_certificate_origin=AppCertificateOrigin.Owner
                       if conf.ssl else AppCertificateOrigin.Self,
                       docker_version="")

    @staticmethod
    def from_toml(path: Path):
        """Build a Context object from a Toml file."""
        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

        return Context(**dataMap)

    def run(self, uuid: UUID, domain_name: str, docker_version: str,
            expires_in: int, config_cert: str, app_cert: str):
        """Complete the context since the app is now running."""
        self.id = uuid
        self.domain_name = domain_name
        self.docker_version = docker_version
        self.expires_in = expires_in
        self.ssl_app_certificate = app_cert

        self.config_cert_path.write_text(config_cert)
        self.app_cert_path.write_text(app_cert)

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
                "encrypted_code": self.encrypted_code,
                "enclave_size": self.enclave_size,
                "expires_in": self.expires_in,
                "python_application": self.python_application,
                "docker_version": self.docker_version,
                "app_certificate_origin": self.app_certificate_origin.value,
                "ssl_app_certificate": self.ssl_app_certificate
            }
            toml.dump(dataMap, f)
