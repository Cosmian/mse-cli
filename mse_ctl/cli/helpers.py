"""Handlers functions."""

from typing import List, Optional
from uuid import UUID

import requests

from mse_ctl.api.app import stop
from mse_ctl.api.auth import Connection
from mse_ctl.api.project import get_app_from_name, get_from_name
from mse_ctl.api.types import App, AppStatus, Project


def get_project_from_name(conn: Connection, name: str) -> Optional[Project]:
    """Get the project from its name."""
    r: requests.Response = get_from_name(conn=conn, project_name=name)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    project = r.json()
    if not project:
        return None

    return Project.from_json_dict(project[0])


def exists_in_project(conn: Connection, project_uuid: UUID, name: str,
                      status: Optional[List[AppStatus]]) -> Optional[App]:
    """Say whether the app exists in the project."""
    r: requests.Response = get_app_from_name(conn=conn,
                                             project_uuid=project_uuid,
                                             app_name=name,
                                             status=status)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    app = r.json()
    if not app:
        return None

    return App.from_json_dict(app[0])


def stop_app(conn: Connection, app_uuid: UUID):
    """Stop the app remotly."""
    r: requests.Response = stop(conn=conn, uuid=app_uuid)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")
