"""mse_cli.cloud.api.user module."""

import requests

from mse_cli.cloud.api.auth import Connection


def me(conn: Connection) -> requests.Response:
    """GET `/users/me`."""
    return conn.get(url="/users/me")
