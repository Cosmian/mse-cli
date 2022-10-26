"""mse_ctl.api.types module."""

import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mse_ctl.conf.app import CodeProtection, EnclaveSize


class AppStatus(Enum):
    """EnclaveStatus enum."""

    Initializing = "Initializing"
    Running = "Running"
    OnError = "OnError"
    Deleted = "Deleted"
    Paused = "Paused"
    Stopped = "Stopped"


class App(BaseModel):
    """App class."""

    uuid: UUID
    name: str
    version: str
    project_uuid: UUID
    owner_uuid: UUID
    domain_name: Optional[str]
    port: Optional[int]
    enclave_version: Optional[str]
    created_at: Optional[datetime.datetime]
    ready_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]
    stopped_at: Optional[datetime.datetime]
    onerror_at: Optional[datetime.datetime]
    status: AppStatus
    enclave_size: EnclaveSize
    code_protection: CodeProtection
    enclave_lifetime: int
    python_application: str
    health_check_endpoint: str

    @staticmethod
    def from_json_dict(json: dict):
        """Build an App object from a json dict."""
        return App(**json)


class BillingPlan(Enum):
    """BillingPlan enum."""

    Free = "Free"
    Essential = "Essential"
    Pro = "Pro"


class Project(BaseModel):
    """App class."""

    uuid: UUID
    name: str
    description: str
    owner_uuid: UUID
    is_default: bool
    billing_plan: BillingPlan
    enclave_version: Optional[str]
    created_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]

    @staticmethod
    def from_json_dict(json: dict):
        """Build a Project object from a json dict."""
        return Project(**json)
