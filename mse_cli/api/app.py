"""mse_cli.api.app module."""

import json
from pathlib import Path
from uuid import UUID

import requests

from mse_cli.api.auth import Connection
from mse_cli.conf.app import AppConf


def new(conn: Connection, conf: AppConf, code_tar_path: Path) -> requests.Response:
    """POST `/apps`."""
    if not code_tar_path.exists():
        raise FileNotFoundError("Can't find tar file!")

    with code_tar_path.open("rb") as fp:
        return conn.post(
            url="/apps",
            files={
                "code": (code_tar_path.name, fp, "application/tar", {"Expires": "0"}),
                "conf": (None, json.dumps(conf.into_payload()), "application/json"),
            },
            timeout=None,
        )


def get(conn: Connection, uuid: UUID) -> requests.Response:
    """GET `/apps/{uuid}`."""
    return conn.get(url=f"/apps/{uuid}")


def remove(conn: Connection, uuid: UUID) -> requests.Response:
    """DELETE `/apps/{uuid}`."""
    return conn.delete(url=f"/apps/{uuid}")


def stop(conn: Connection, uuid: UUID) -> requests.Response:
    """POST `/apps/{uuid}`."""
    return conn.post(url=f"/apps/{uuid}/stop")


def log(conn: Connection, uuid: UUID) -> requests.Response:
    """GET `/apps/{uuid}/logs`."""
    return conn.get(url=f"/apps/{uuid}/logs")
