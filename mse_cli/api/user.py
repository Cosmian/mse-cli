"""mse_cli.api.user module."""

import requests

from mse_cli.api.auth import Connection


def me(conn: Connection) -> requests.Response:
    """GET `/users/me`."""
    return conn.get(url="/users/me")
