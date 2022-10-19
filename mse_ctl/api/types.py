"""mse_ctl.api.types module."""

import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mse_ctl.conf.enclave import CodeProtection, EnclaveSize


class EnclaveStatus(Enum):
    """EnclaveStatus enum."""

    Initializing = "Initializing"
    Running = "Running"
    OnError = "OnError"
    Deleted = "Deleted"


class Enclave(BaseModel):
    """Enclave class."""

    uuid: UUID
    service_name: str
    service_version: str
    owner_uuid: UUID
    domain_name: Optional[str]
    port: Optional[int]
    enclave_version: Optional[str]
    created_at: Optional[datetime.datetime]
    ready_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]
    status: EnclaveStatus
    enclave_size: EnclaveSize
    code_protection: CodeProtection
    enclave_lifetime: int
    python_flask_module: str
    python_flask_variable_name: str
    health_check_endpoint: str

    @staticmethod
    def from_json_dict(json: dict):
        """Build a Enclave object from a json dict."""
        return Enclave(**json)
