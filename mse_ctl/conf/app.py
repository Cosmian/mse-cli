"""App configuration file module."""

import os
from enum import Enum
from pathlib import Path

import toml
from pydantic import BaseModel


class CodeProtection(str, Enum):
    """Code protection."""

    Encrypted = "encrypted"
    Plaintext = "plaintext"


class EnclaveSize(str, Enum):
    """Enclave size."""

    G1 = "1G"
    G2 = "2G"
    G4 = "4G"
    G8 = "8G"


class AppConf(BaseModel):
    """Definition of an app by a user."""

    # Name of the mse instance
    name: str
    # Version of the mse instance
    version: str

    # Name of the parent project
    project: str

    # Location of the code (a path or an url)
    code_location: str
    # Wether the code is encrypted or not
    code_protection: CodeProtection

    # Size of the enclave
    enclave_size: EnclaveSize
    # Lifetime of the spawned enclave
    enclave_lifetime: int

    # from python_flask_module import python_flask_variable_name
    python_application: str

    # Endpoint to use to check if the application is up and sane
    health_check_endpoint: str

    @property
    def python_module(self):
        """Get the python module from python_application."""
        split_str = self.python_application.split(":")
        assert len(split_str) == 2
        return split_str[0]

    @property
    def python_variable(self):
        """Get the python variable from python_application."""
        split_str = self.python_application.split(":")
        assert len(split_str) == 2
        return split_str[1]

    @property
    def service_identifier(self):
        """Get the service identifier."""
        return f"{self.name}-{self.version}"

    @staticmethod
    def from_toml():
        """Build a AppConf object from a Toml file."""
        with open(Path(os.getcwd()) / "mse.toml", encoding="utf8") as f:
            dataMap = toml.load(f)

            return AppConf(**dataMap)

    def save(self, folder: Path):
        """Dump the current object to a file."""
        with open(folder / "mse.toml", "w", encoding="utf8") as f:
            dataMap = {
                "name": self.name,
                "version": self.version,
                "project": self.project,
                "code_location": self.code_location,
                "code_protection": self.code_protection.value,
                "enclave_size": self.enclave_size.value,
                "enclave_lifetime": self.enclave_lifetime,
                "python_application": self.python_application,
                "health_check_endpoint": self.health_check_endpoint
            }
            toml.dump(dataMap, f)

    @staticmethod
    def default(name: str, code_path: Path):
        """Generate a default configuration."""
        dataMap = {
            "name": name,
            "version": "0.1.0",
            "project": "default",
            "code_location": str(code_path) + "/code",
            "code_protection": "plaintext",
            "enclave_size": "1G",
            "enclave_lifetime": 1,
            "python_application": "app:app",
            "health_check_endpoint": "/"
        }

        return AppConf(**dataMap)
