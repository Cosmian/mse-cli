"""mse_cli.core.no_sgx_docker module."""

from pathlib import Path
from typing import ClassVar, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from mse_cli.core.sgx_docker import SgxDockerConfig


class NoSgxDockerConfig(BaseModel):
    """Definition of an mse docker running on a non-sgx hardware."""

    subject: str
    subject_alternative_name: str
    expiration_date: Optional[int]
    size: int
    app_id: UUID
    application: str

    app_mountpoint: ClassVar[str] = "/opt/input"
    entrypoint: ClassVar[str] = "mse-run"

    def cmd(self) -> List[str]:
        """Serialize the docker command args."""
        command = [
            "--size",
            f"{self.size}M",
            "--subject",
            self.subject,
            "--san",
            self.subject_alternative_name,
            "--id",
            str(self.app_id),
            "--application",
            self.application,
            "--dry-run",
        ]

        if self.expiration_date:
            command.append("--expiration")
            command.append(str(self.expiration_date))

        return command

    def volumes(self, app_path: Path) -> Dict[str, Dict[str, str]]:
        """Define the docker volumes."""
        return {
            f"{app_path.resolve()}": {
                "bind": NoSgxDockerConfig.app_mountpoint,
                "mode": "rw",
            }
        }

    @staticmethod
    def from_sgx(docker_config: SgxDockerConfig):
        """Load from a SgxDockerConfig object."""
        return NoSgxDockerConfig(
            subject=docker_config.subject,
            subject_alternative_name=docker_config.subject_alternative_name,
            expiration_date=docker_config.expiration_date,
            size=docker_config.size,
            app_id=docker_config.app_id,
            application=docker_config.application,
        )
