"""mse_ctl.api.user module."""

import requests

from mse_ctl.api.auth import Connection


def me(conn: Connection) -> requests.Response:
    """GET `/users/me`."""
    return conn.get(url=f"/users/me")
