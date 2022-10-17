"""mse_ctl.api.types module."""

import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from enum import Enum


class EnclaveStatus(Enum):
    """EnclaveStatus enum."""

    Initializing = "Initializing"
    Running = "Running"
    OnError = "OnError"
    Deleted = "Deleted"


class Enclave(BaseModel):
    """Enclave class."""

    uuid: UUID
    name: str
    owner_uuid: UUID
    domain_name: Optional[str]
    version: Optional[str]
    created_at: Optional[datetime.datetime]
    ready_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]
    status: EnclaveStatus

    @staticmethod
    def from_json_dict(json: dict):
        """Build a Enclave object from a json dict."""
        return Enclave(**json)
