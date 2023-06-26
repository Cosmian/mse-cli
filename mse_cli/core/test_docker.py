"""mse_cli_core.test_docker module."""

from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Tuple

from pydantic import BaseModel


class TestDockerConfig(BaseModel):
    """Definition of a running test docker configuration."""

    port: int
    code: Path
    application: str
    sealed_secrets: Optional[Path]
    secrets: Optional[Path]

    secret_mountpoint: ClassVar[str] = "/root/.cache/mse/secrets.json"
    sealed_secrets_mountpoint: ClassVar[str] = "/root/.cache/mse/sealed_secrets.json"

    code_mountpoint: ClassVar[str] = "/mse-app"
    entrypoint: ClassVar[str] = "mse-test"

    def cmd(self) -> List[str]:
        """Serialize the docker command args."""
        return ["--application", self.application, "--debug"]

    def ports(self) -> Dict[str, Tuple[str, str]]:
        """Define the docker ports."""
        return {f"{self.port}/tcp": ("127.0.0.1", str(self.port))}

    def volumes(self) -> Dict[str, Dict[str, str]]:
        """Define the docker volumes."""
        v = {
            f"{self.code.resolve()}": {
                "bind": TestDockerConfig.code_mountpoint,
                "mode": "rw",
            },
        }

        if self.secrets:
            v[f"{self.secrets.resolve()}"] = {
                "bind": TestDockerConfig.secret_mountpoint,
                "mode": "rw",
            }

        if self.sealed_secrets:
            v[f"{self.sealed_secrets.resolve()}"] = {
                "bind": TestDockerConfig.sealed_secrets_mountpoint,
                "mode": "rw",
            }

        return v
