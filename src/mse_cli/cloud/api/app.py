"""mse_cli.api.app module."""

import json
from pathlib import Path
from uuid import UUID

import requests

from mse_cli.cloud.api.auth import Connection
from mse_cli.core.conf import AppConf


def new(conn: Connection, conf: AppConf, code_tar_path: Path) -> requests.Response:
    """POST `/apps`."""
    if not code_tar_path.exists():
        raise FileNotFoundError("Can't find tar file!")

    with code_tar_path.open("rb") as fp:
        return conn.post(
            url="/apps",
            files={
                "code": (code_tar_path.name, fp, "application/tar", {"Expires": "0"}),
                "conf": (
                    None,
                    json.dumps(conf.into_cloud_payload()),
                    "application/json",
                ),
            },
            timeout=None,
        )


def metrics(conn: Connection, app_id: UUID) -> requests.Response:
    """GET `/apps/{app_id}/metrics`."""
    return conn.get(url=f"/apps/{app_id}/metrics")


def get(conn: Connection, app_id: UUID) -> requests.Response:
    """GET `/apps/{app_id}`."""
    return conn.get(url=f"/apps/{app_id}")


def default(conn: Connection) -> requests.Response:
    """GET `/apps/default`."""
    return conn.get(url="/apps/default")


def remove(conn: Connection, app_id: UUID) -> requests.Response:
    """DELETE `/apps/{app_id}`."""
    return conn.delete(url=f"/apps/{app_id}")


def stop(conn: Connection, app_id: UUID) -> requests.Response:
    """POST `/apps/{app_id}`."""
    return conn.post(url=f"/apps/{app_id}/stop")


def log(conn: Connection, app_id: UUID) -> requests.Response:
    """GET `/apps/{app_id}/logs`."""
    return conn.get(url=f"/apps/{app_id}/logs")
