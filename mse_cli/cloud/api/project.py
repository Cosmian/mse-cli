"""mse_cli.cloud.api.project module."""

from typing import List, Optional
from uuid import UUID

import requests

from mse_cli.cloud.api.auth import Connection
from mse_cli.cloud.api.types import AppStatus


def list_apps(
    conn: Connection, project_id: Optional[UUID], status: Optional[List[AppStatus]]
) -> requests.Response:
    """GET `/apps`."""
    return conn.get(
        url="/apps",
        params={
            "status": ",".join(map(lambda s: s.value, status)) if status else None,
            "project": str(project_id) if project_id else None,
        },
    )


def get_app_from_name(
    conn: Connection,
    project_id: UUID,
    app_name: str,
    status: Optional[List[AppStatus]],
) -> requests.Response:
    """GET `/apps?name=str&status=s1,s2,s3`."""
    return conn.get(
        url="/apps",
        params={
            "name": app_name,
            "status": ",".join(map(lambda s: s.value, status)) if status else None,
            "project": str(project_id),
        },
    )


def get(conn: Connection, project_id: UUID) -> requests.Response:
    """GET `/projects/{id}`."""
    return conn.get(url=f"/projects/{project_id}")


def get_from_name(conn: Connection, project_name: str) -> requests.Response:
    """GET `/projects?name=str`."""
    return conn.get(url="/projects", params={"name": project_name})
