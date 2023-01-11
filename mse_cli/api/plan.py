"""mse_cli.api.plan module."""

import requests

from mse_cli.api.auth import Connection


def get(conn: Connection, name: str) -> requests.Response:
    """GET `/plans/{name}`."""
    return conn.get(url=f"/plans/{name}")
