"""mse_cli.api.hardware module."""

import requests

from mse_cli.api.auth import Connection


def get(conn: Connection, name: str) -> requests.Response:
    """GET `/hardwares/{name}`."""
    return conn.get(url=f"/hardwares/{name}")
