"""Enclave configuration file module."""

from enum import Enum
import toml
import os
from pathlib import Path

from pydantic import BaseModel


class CodeMode(Enum):
    """Code mode."""

    Encrypted = "encrypted"
    Plaintext = "plaintext"


class EnclaveSize(Enum):
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
    code_mode: CodeMode

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
        return f"{self.service_name}-{self.service_version}"

    @staticmethod
    def from_toml():
        """Build a EnclaveConf object from a Toml file."""
        with open(Path(os.getcwd()) / "mse.toml") as f:
            dataMap = toml.load(f)

            return EnclaveConf(**dataMap)
