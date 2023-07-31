"""mse_cli.cloud.api.hardware module."""

import requests

from mse_cli.cloud.api.auth import Connection


def get(conn: Connection, name: str) -> requests.Response:
    """GET `/hardwares/{name}`."""
    return conn.get(url=f"/hardwares/{name}")
