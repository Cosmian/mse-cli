"""Enclave configuration file module."""

from enum import Enum
import toml
import os
from pathlib import Path

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


class EnclaveConf(BaseModel):
    """Definition of an enclave by a user."""

    # Name of the mse instance
    service_name: str
    # Version of the mse instance
    service_version: str

    # Location of the code (a path or an url)
    code_location: str
    # Wether the code is encrypted or not
    code_protection: CodeProtection

    # Size of the enclave
    enclave_size: EnclaveSize
    # Lifetime of the spawned enclave
    enclave_lifetime: int

    # from python_flask_module import python_flask_variable_name
    python_flask_module: str
    python_flask_variable_name: str

    # Endpoint to use to check if the application is up and sane
    health_check_endpoint: str

    @property
    def service_identifier(self):
        """Get the service identifier."""
        return f"{self.service_name}-{self.service_version}"

    @staticmethod
    def from_toml():
        """Build a EnclaveConf object from a Toml file."""
        with open(Path(os.getcwd()) / "mse.toml") as f:
            dataMap = toml.load(f)

            return EnclaveConf(**dataMap)

    def save(self, folder: Path):
        """Dump the current object to a file."""
        with open(folder / "mse.toml", "w") as f:
            dataMap = {
                "service_name": self.service_name,
                "service_version": self.service_version,
                "code_location": self.code_location,
                "code_protection": self.code_protection.value,
                "enclave_size": self.enclave_size.value,
                "enclave_lifetime": self.enclave_lifetime,
                "python_flask_module": self.python_flask_module,
                "python_flask_variable_name": self.python_flask_variable_name,
                "health_check_endpoint": self.health_check_endpoint
            }
            toml.dump(dataMap, f)

    @staticmethod
    def default(name: str, code_path: Path):
        """Generate a default configuration."""
        dataMap = {
            "service_name": name,
            "service_version": "0.1.0",
            "code_location": str(code_path),
            "code_protection": "plaintext",
            "enclave_size": "1G",
            "enclave_lifetime": 1,
            "python_flask_module": "app",
            "python_flask_variable_name": "app",
            "health_check_endpoint": "/"
        }

        return EnclaveConf(**dataMap)
