"""Context file."""

from datetime import datetime
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

import toml
from pydantic import BaseModel, validator
from mse_lib_crypto.xsalsa20_poly1305 import random_key

from mse_ctl import MSE_CONF_DIR
from mse_ctl.api.types import SSLCertificateOrigin
from mse_ctl.conf.app import AppConf


class ContextInstance(BaseModel):
    """Part of the context coming from the instanciation."""

    # Unique id of the app
    id: UUID
    # Domain name of the configuration server
    config_domain_name: str
    # Size of the enclave determine from the plan
    enclave_size: int
    # Shutdown date of the spawned enclave
    expires_at: datetime
    # The mse-docker version
    docker_version: str
    # The origin of the app SSL certificate
    ssl_certificate_origin: SSLCertificateOrigin


class ContextConf(BaseModel):
    """Part of the context coming from the app conf."""

    # Name of the mse app
    name: str
    # Version of the mse app
    version: str
    # Project parent of the app
    project: str
    # Symetric key used to encrypt the code
    code_sealed_key: bytes
    # from python_flask_module import python_flask_variable_name
    python_application: str
    # The certificate of the app if origin = Owner
    ssl_app_certificate: Optional[str] = None

    @validator('code_sealed_key', pre=True, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def set_code_sealed_key(cls, v, values, **kwargs):
        """Set code_sealed_key from a value for pydantic."""
        return bytes.fromhex(v) if isinstance(v, str) else v


class Context(BaseModel):
    """Definition of a mse context."""

    # The version of context file
    version: str = "1.0"
    # The config of the app
    config: ContextConf
    # The mse app instance parameters
    instance: Optional[ContextInstance] = None

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
        assert self.instance
        return path / (str(self.instance.id) + ".mse")

    @property
    def workspace(self) -> Path:
        """Get the workspace path and create it."""
        path = Path(
            tempfile.gettempdir()) / f"{self.config.name}-{self.config.version}"
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def from_app_conf(conf: AppConf):
        """Build a Context object from an app conf."""
        cert = conf.ssl.certificate if conf.ssl else None

        context = Context(
            config=ContextConf(name=conf.name,
                               version=conf.version,
                               project=conf.project,
                               python_application=conf.code.python_application,
                               code_sealed_key=bytes(random_key()).hex(),
                               ssl_app_certificate=cert))

        if cert:
            context.app_cert_path.write_text(cert)

        return context

    @staticmethod
    def from_toml(path: Path):
        """Build a Context object from a Toml file."""
        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

        return Context(**dataMap)

    def run(self, uuid: UUID, enclave_size: int, config_domain_name: str,
            docker_version: str, expires_at: datetime,
            ssl_certificate_origin: SSLCertificateOrigin):
        """Complete the context since the app is now running."""
        self.instance = ContextInstance(
            id=uuid,
            config_domain_name=config_domain_name,
            enclave_size=enclave_size,
            docker_version=docker_version,
            expires_at=expires_at,
            ssl_certificate_origin=ssl_certificate_origin,
        )

    def save(self):
        """Dump the current object to a file."""
        with open(self.exported_path, "w", encoding="utf8") as f:
            dataMap: Dict[str, Any] = {
                "version": self.version,
                "config": {
                    "name": self.config.name,
                    "version": self.config.version,
                    "project": self.config.project,
                    "python_application": self.config.python_application,
                    "code_sealed_key": bytes(self.config.code_sealed_key).hex()
                }
            }

            if self.config.ssl_app_certificate:
                dataMap["config"][
                    "ssl_app_certificate"] = self.config.ssl_app_certificate

            if self.instance:
                origin = self.instance.ssl_certificate_origin.value
                dataMap["instance"] = {
                    "id": str(self.instance.id),
                    "config_domain_name": self.instance.config_domain_name,
                    "enclave_size": self.instance.enclave_size,
                    "expires_at": str(self.instance.expires_at),
                    "docker_version": self.instance.docker_version,
                    "ssl_certificate_origin": origin,
                }

            toml.dump(dataMap, f)
