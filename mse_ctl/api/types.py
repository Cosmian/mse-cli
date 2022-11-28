"""mse_ctl.api.types module."""

import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AppStatus(Enum):
    """EnclaveStatus enum."""

    Initializing = "initializing"
    Running = "running"
    OnError = "on_error"
    Deleted = "deleted"
    Stopped = "stopped"


class SSLCertificateOrigin(str, Enum):
    """SSLCertificateOrigin enum."""

    Self = "self"
    Owner = "owner"
    Operator = "operator"


class App(BaseModel):
    """App class."""

    uuid: UUID
    name: str
    version: str
    project_uuid: UUID
    owner_uuid: UUID
    domain_name: str
    config_domain_name: str
    docker_version: str
    created_at: datetime.datetime
    ready_at: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime]
    stopped_at: Optional[datetime.datetime]
    onerror_at: Optional[datetime.datetime]
    status: AppStatus
    plan: str
    ssl_certificate_origin: SSLCertificateOrigin
    expires_at: datetime.datetime
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
    stripe_customer_id: Optional[str]
    stripe_payment_method_id: Optional[str]
    enclave_version: Optional[str]
    created_at: datetime.datetime
    deleted_at: Optional[datetime.datetime]

    @staticmethod
    def from_json_dict(json: dict):
        """Build a Project object from a json dict."""
        return Project(**json)


class Plan(BaseModel):
    """Plan class."""

    name: str
    memory: int
    cores: float
    price: float

    @staticmethod
    def from_json_dict(json: dict):
        """Build a Plan object from a json dict."""
        return Plan(**json)
