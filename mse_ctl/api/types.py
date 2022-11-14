"""mse_ctl.api.types module."""

import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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
    domain_name: str
    docker_version: Optional[str]
    created_at: Optional[datetime.datetime]
    ready_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]
    stopped_at: Optional[datetime.datetime]
    onerror_at: Optional[datetime.datetime]
    status: AppStatus
    plan: str
    encrypted_code: bool
    delegated_ssl: bool
    shutdown_delay: int
    python_application: str
    health_check_endpoint: str

    @staticmethod
    def from_json_dict(json: dict):
        """Build an App object from a json dict."""
        return App(**json)


class Project(BaseModel):
    """Project class."""

    uuid: UUID
    name: str
    description: str
    owner_uuid: UUID
    is_default: bool
    enclave_version: Optional[str]
    created_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]

    @staticmethod
    def from_json_dict(json: dict):
        """Build a Project object from a json dict."""
        return Project(**json)


class Plan(BaseModel):
    """Plan class."""
    name: str
    memory: int
    cores: int
    price: float
    created_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]

    @staticmethod
    def from_json_dict(json: dict):
        """Build a Plan object from a json dict."""
        return Plan(**json)