"""mse_ctl.api.enclave module."""

from pathlib import Path
from typing import List, Optional
from uuid import UUID
import requests

from mse_ctl.api.auth import Connection


def new(conn: Connection, name: str) -> requests.Response:
    """POST `/enclaves`."""
    return conn.post(url="/enclaves", json={
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
