"""mse_ctl.api.enclave module."""

from pathlib import Path
from typing import List, Optional
from uuid import UUID
import requests

from mse_ctl.api.auth import Connection


def new(conn: Connection, name: str, code_tar_path: Path) -> requests.Response:
    """POST `/enclaves`."""
    if not code_tar_path.exists():
        raise FileNotFoundError("Can't find tar file!")

    with code_tar_path.open("rb") as fp:
        return conn.post(url="/enclaves",
                         files={
                             "file":
                                 (code_tar_path.name, fp, "application/tar", {
                                     "Expires": "0"
                                 })
                         },
                         timeout=None,
                         json={
                             "name": name,
                         })


def list(conn: Connection) -> requests.Response:
    """GET `/enclaves`."""
    return conn.get(url="/enclaves")


def get(conn: Connection, uuid: UUID) -> requests.Response:
    """GET `/enclaves/{uuid}`."""
    return conn.get(url=f"/enclaves/{uuid}")


def remove(conn: Connection, uuid: UUID) -> requests.Response:
    """DELETE `/enclaves/{uuid}`."""
    return conn.delete(url=f"/enclaves/{uuid}")
