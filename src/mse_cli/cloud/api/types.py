"""mse_cli.cloud.api.types module."""

import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class AppStatus(Enum):
    """EnclaveStatus enum."""

    Spawning = "spawning"
    Initializing = "initializing"
    Running = "running"
    OnError = "on_error"
    Stopped = "stopped"


class SSLCertificateOrigin(Enum):
    """SSLCertificateOrigin enum."""

    Self = "self"
    Owner = "owner"
    Operator = "operator"


class App(BaseModel):
    """App model."""

    id: UUID
    name: str
    project_id: UUID
    owner_id: str
    domain_name: str
    config_domain_name: str
    docker: str
    created_at: datetime.datetime
    ready_at: Optional[datetime.datetime]
    stopped_at: Optional[datetime.datetime]
    status: AppStatus
    hardware_name: str
    ssl_certificate_origin: SSLCertificateOrigin
    expires_at: datetime.datetime
    python_application: str
    healthcheck_endpoint: str

    def is_terminated(self):
        """Check if the app is terminated (success or failure)."""
        return self.status in (AppStatus.OnError, AppStatus.Stopped)

    @staticmethod
    def from_dict(dct: Dict[str, Any]):
        """Build an App object from a dictionary."""
        return App(**dct)


class PartialApp(BaseModel):
    """App model (partial fields)."""

    id: UUID
    name: str
    domain_name: str
    created_at: datetime.datetime
    ready_at: Optional[datetime.datetime]
    stopped_at: Optional[datetime.datetime]
    status: AppStatus
    hardware_name: str

    @staticmethod
    def from_dict(dct: Dict[str, Any]):
        """Build an PartialApp object from a dictionary."""
        return PartialApp(**dct)


class DefaultAppConfig(BaseModel):
    """Default app config."""

    project: str
    docker: str
    hardware: str

    @staticmethod
    def from_dict(dct: Dict[str, Any]):
        """Build an DefaultAppConfig object from a dictionary."""
        return DefaultAppConfig(**dct)


class Project(BaseModel):
    """Project model."""

    id: UUID
    name: str
    description: str
    owner_id: str
    is_default: bool
    stripe_customer_id: Optional[str]
    stripe_payment_method_id: Optional[str]
    created_at: datetime.datetime
    deleted_at: Optional[datetime.datetime]

    @staticmethod
    def from_dict(dct: Dict[str, Any]):
        """Build a Project object from a dictionary."""
        return Project(**dct)


class Hardware(BaseModel):
    """Hardware model."""

    name: str
    memory: int
    cores: int
    enclave_size: int

    @staticmethod
    def from_dict(dct: Dict[str, Any]):
        """Build a Hardware object from a dictionary."""
        return Hardware(**dct)


class User(BaseModel):
    """User model."""

    id: str
    given_name: str
    family_name: str
    email: str
    created_at: datetime.datetime
    configured: bool
    email_verified: bool

    @staticmethod
    def from_dict(dct: Dict[str, Any]):
        """Build a User object from a dictionnary."""
        return User(**dct)
