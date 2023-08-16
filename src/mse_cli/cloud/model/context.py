"""mse_cli.cloud.model.context module."""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import toml
from mse_lib_crypto.xsalsa20_poly1305 import random_key
from pydantic import BaseModel, validator

from mse_cli import MSE_CONF_DIR
from mse_cli.cloud.api.types import SSLCertificateOrigin
from mse_cli.core.conf import AppConf


class ContextInstance(BaseModel):
    """Part of the context coming from the instanciation."""

    # Unique id of the app
    id: UUID
    # Domain name of the configuration server
    config_domain_name: str
    # Size of the enclave determine from the hardware configuration
    enclave_size: int
    # Shutdown date of the spawned enclave
    expires_at: datetime
    # The origin of the app SSL certificate
    ssl_certificate_origin: SSLCertificateOrigin
    # The nounces of the encrypted files
    nonces: Dict[str, bytes]

    @validator("nonces", pre=True, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def set_nonces(cls, v, values, **kwargs):
        """Set nonces from a value for pydantic."""
        if isinstance(v, dict):
            d = {}
            for key in v:
                if isinstance(v[key], str):
                    d[key] = bytes.fromhex(v[key])
                else:
                    d[key] = v[key]
            return d
        return v


class ContextConf(BaseModel):
    """Part of the context coming from the app conf."""

    # Name of the mse app
    name: str
    # Project parent of the app
    project: str
    # Symetric key used to encrypt the code
    code_secret_key: bytes
    # Mse docker to use
    docker: str
    # from python_flask_module import python_flask_variable_name
    python_application: str
    # The certificate of the app if origin = Owner
    ssl_app_certificate: Optional[str] = None
    # The tests path of the application
    tests: Path
    # The command to test the application
    tests_cmd: str
    # The package to install before testing the application
    tests_requirements: List[str]

    @validator("code_secret_key", pre=True, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def set_code_secret_key(cls, v, values, **kwargs):
        """Set code_secret_key from a value for pydantic."""
        return bytes.fromhex(v) if isinstance(v, str) else v


class Context(BaseModel):
    """Definition of a mse context."""

    # The version of context file
    version: str = "2.0"
    # The config of the app
    config: ContextConf
    # The mse app instance parameters
    instance: Optional[ContextInstance] = None
    # The workspace used when deploying the app
    workspace: Path

    @staticmethod
    def get_root_dirpath() -> Path:
        """Get the root path containing all the contexts."""
        path = MSE_CONF_DIR / "context"
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def get_dirpath(uuid: UUID, create=True) -> Path:
        """Get the directory path of that context."""
        path = Context.get_root_dirpath() / str(uuid)
        if create:
            os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def get_context_filename():
        """Get the filename of the context file."""
        return "context.mse"

    @staticmethod
    def get_tar_code_filename():
        """Get the filename of the code tarball."""
        return "app.tar"

    @staticmethod
    def get_context_filepath(uuid: UUID, create=True) -> Path:
        """Get the path of the context file."""
        return Context.get_dirpath(uuid, create) / Context.get_context_filename()

    @property
    def path(self) -> Path:
        """Get the path of the context file."""
        assert self.instance
        return Context.get_context_filepath(self.instance.id)

    @property
    def docker_log_path(self):
        """Get the path to store the docker logs."""
        return self.workspace / "docker.log"

    @property
    def config_cert_path(self):
        """Get the path to store the certificate."""
        return self.workspace / "ratls.pem"

    @property
    def app_cert_path(self):
        """Get the path to store the certificate."""
        return self.workspace / "fullchain.pem"

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
        return self.workspace / Context.get_tar_code_filename()

    @staticmethod
    def clean(uuid: UUID, ignore_errors: bool = False):
        """Remove the context directory."""
        shutil.rmtree(
            Context.get_dirpath(uuid, create=False), ignore_errors=ignore_errors
        )

    @staticmethod
    def from_app_conf(conf: AppConf, workspace: Optional[Path] = None):
        """Build a Context object from an app conf."""
        cloud_conf = conf.cloud_or_raise()
        cert = cloud_conf.ssl.certificate_data if cloud_conf.ssl else None

        if not workspace:
            workspace = Path(tempfile.mkdtemp())
        else:
            workspace = workspace.expanduser().resolve()

        context = Context(
            workspace=workspace,
            config=ContextConf(
                name=conf.name,
                project=cloud_conf.project,
                python_application=conf.python_application,
                docker=cloud_conf.docker,
                code_secret_key=random_key(),
                tests=cloud_conf.tests,
                tests_cmd=conf.tests_cmd,
                tests_requirements=conf.tests_requirements,
                ssl_app_certificate=cert,
            ),
        )

        if cert:
            context.app_cert_path.write_text(cert)

        return context

    @staticmethod
    def load(path: Path, workspace: Optional[Path] = None):
        """Build a Context object from a toml file."""
        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

        if not workspace:
            workspace = Path(tempfile.mkdtemp())
        else:
            workspace = workspace.expanduser().resolve()

        dataMap["workspace"] = workspace

        return Context(**dataMap)

    def run(
        self,
        app_id: UUID,
        enclave_size: int,
        config_domain_name: str,
        expires_at: datetime,
        ssl_certificate_origin: SSLCertificateOrigin,
        nonces: Dict[str, bytes],
    ):
        """Complete the context since the app is now running."""
        self.instance = ContextInstance(
            id=app_id,
            config_domain_name=config_domain_name,
            enclave_size=enclave_size,
            expires_at=expires_at,
            ssl_certificate_origin=ssl_certificate_origin,
            nonces=nonces,
        )

    def save(self) -> None:
        """Dump the current object to a file."""
        with open(self.path, "w", encoding="utf8") as f:
            dataMap: Dict[str, Any] = {
                "version": self.version,
                "config": {
                    "name": self.config.name,
                    "project": self.config.project,
                    "docker": self.config.docker,
                    "python_application": self.config.python_application,
                    "tests": str(self.config.tests),
                    "tests_cmd": self.config.tests_cmd,
                    "tests_requirements": self.config.tests_requirements,
                    "code_secret_key": bytes(self.config.code_secret_key).hex(),
                },
            }

            if self.config.ssl_app_certificate:
                dataMap["config"][
                    "ssl_app_certificate"
                ] = self.config.ssl_app_certificate

            if self.instance:
                origin = self.instance.ssl_certificate_origin.value
                nonces = dict(
                    map(
                        lambda item: (item[0], bytes(item[1]).hex()),
                        self.instance.nonces.items(),
                    )
                )

                dataMap["instance"] = {
                    "id": str(self.instance.id),
                    "config_domain_name": self.instance.config_domain_name,
                    "enclave_size": self.instance.enclave_size,
                    "expires_at": str(self.instance.expires_at),
                    "ssl_certificate_origin": origin,
                    "nonces": nonces,
                }

            toml.dump(dataMap, f)

        # Also save the tar code in the context folder
        if self.instance:
            shutil.copyfile(
                self.tar_code_path,
                Context.get_dirpath(self.instance.id) / Context.get_tar_code_filename(),
            )
