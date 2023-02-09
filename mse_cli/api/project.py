"""mse_cli.api.project module."""

from typing import List, Optional
from uuid import UUID

import requests

from mse_cli.api.auth import Connection
from mse_cli.api.types import AppStatus


def list_apps(
    conn: Connection, project_uuid: UUID, status: Optional[List[AppStatus]]
) -> requests.Response:
    """GET `/projects/{uuid}/apps`."""
    return conn.get(
        url=f"/projects/{str(project_uuid)}/apps",
        params={"status": ",".join(map(lambda s: s.value, status)) if status else None},
    )


def get_app_from_name(
    conn: Connection,
    project_uuid: UUID,
    app_name: str,
    status: Optional[List[AppStatus]],
) -> requests.Response:
    """GET `/projects/{uuid}/apps?name=str&status=s1,s2,s3`."""
    return conn.get(
        url=f"/projects/{str(project_uuid)}/apps",
        params={
            "name": app_name,
            "status": ",".join(map(lambda s: s.value, status)) if status else None,
        },
    )


def get(conn: Connection, project_uuid: UUID) -> requests.Response:
    """GET `/projects/{uuid}`."""
    return conn.get(url=f"/projects/{project_uuid}")


def get_from_name(conn: Connection, project_name: str) -> requests.Response:
    """GET `/projects?name=str`."""
    return conn.get(url="/projects", params={"name": project_name})
