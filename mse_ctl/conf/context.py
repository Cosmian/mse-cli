"""Context file."""

from datetime import datetime
import os
import tempfile
from pathlib import Path
from uuid import UUID

import toml
from pydantic import BaseModel, validator
from mse_lib_crypto.xsalsa20_poly1305 import random_key

from mse_ctl import MSE_CONF_DIR
from mse_ctl.api.types import SSLCertificateOrigin
from mse_ctl.conf.app import AppConf


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
    # Domain name of the configuration server
    config_domain_name: str
    # Domain name of the app
    domain_name: str
    # Symetric used to encrypt the code
    symkey: bytes
    # Whether the code is encrypted or not
    encrypted_code: bool
    # Size of the enclave
    enclave_size: str
    # Shutdown date of the spawned enclave
    expires_at: datetime
    # from python_flask_module import python_flask_variable_name
    python_application: str
    # The mse-docker version
    docker_version: str
    # The certificate of the app (self-signed or signed)
    ssl_app_certificate: str
    # Whether the certificate has been provided by the app owner
    ssl_certificate_origin: SSLCertificateOrigin

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
        return Context(  # TODO: could we generate context from app and not appconf?
            name=conf.name,
            version=conf.version,
            project=conf.project,
            id="00000000-0000-0000-0000-000000000000",
            config_domain_name="",
            domain_name="",
            encrypted_code=conf.code.encrypted,
            enclave_size=enclave_size,
            expires_at=0,  # TODO
            python_application=conf.code.python_application,
            symkey=bytes(random_key()).hex(),
            ssl_app_certificate="",
            ssl_certificate_origin=SSLCertificateOrigin.Owner
            if conf.ssl else SSLCertificateOrigin.Self,  # TODO
            docker_version="")

    @staticmethod
    def from_toml(path: Path):
        """Build a Context object from a Toml file."""
        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

        return Context(**dataMap)

    def run(self, uuid: UUID, config_domain_name: str, domain_name: str,
            docker_version: str, expires_at: datetime, config_cert: str,
            app_cert: str, ssl_certificate_origin: SSLCertificateOrigin):
        """Complete the context since the app is now running."""
        self.id = uuid
        self.config_domain_name = config_domain_name
        self.domain_name = domain_name
        self.docker_version = docker_version
        self.expires_at = expires_at
        self.ssl_app_certificate = app_cert
        self.ssl_certificate_origin = ssl_certificate_origin

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
                "config_domain_name": self.config_domain_name,
                "domain_name": self.domain_name,
                "symkey": bytes(self.symkey).hex(),
                "encrypted_code": self.encrypted_code,
                "enclave_size": self.enclave_size,
                "expires_at": self.expires_at,
                "python_application": self.python_application,
                "docker_version": self.docker_version,
                "ssl_certificate_origin": self.ssl_certificate_origin.value,
                "ssl_app_certificate": self.ssl_app_certificate
            }
            toml.dump(dataMap, f)

    # TODO: add mse-ctl-version field
