"""mse_cli.home.command.sgx_operator.status module."""

from datetime import datetime

import requests

from mse_cli.core.sgx_docker import SgxDockerConfig
from mse_cli.home.command.helpers import (
    get_app_container,
    get_client_docker,
    is_running,
)
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("status", help="print the MSE docker status")

    parser.add_argument(
        "name",
        type=str,
        help="name of the application",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    client = get_client_docker()
    container = get_app_container(client, args.name)

    docker = SgxDockerConfig.load(container.attrs, container.labels)

    expires_at = datetime.fromtimestamp(docker.expiration_date)
    remaining_days = expires_at - datetime.now()

    LOG.info("    App name = %s", args.name)
    LOG.info("Enclave size = %dM", docker.size)
    LOG.info(" Common name = %s", docker.subject_alternative_name)
    LOG.info("        Port = %d", docker.port)
    LOG.info(" Healthcheck = %s", docker.healthcheck)
    LOG.info(
        "      Status = %s",
        app_state(docker.host, docker.port, docker.healthcheck)
        if is_running(container)
        else container.status,
    )
    LOG.info(
        "  Started at = %s",
        container.attrs["State"]["StartedAt"],
    )
    LOG.info(
        "  Expires at = %s (%d days remaining)",
        expires_at.astimezone(),
        remaining_days.days,
    )


def app_state(host: str, port: int, healthcheck_endpoint: str) -> str:
    """Determine the application state by querying it."""
    try:
        # Note: the configuration server allows any path
        # So: `healthcheck_endpoint`` does not exist but it's process as /
        # We can there do one query for the application and the configuration server
        response = requests.get(
            f"https://{host}:{port}{healthcheck_endpoint}",
            verify=False,
            timeout=60,
        )

        if response.status_code == 503:
            return "initializing"

        if response.status_code == 500:
            return "on error"

        if response.status_code == 200 and "Mse-Status" in response.headers:
            return "waiting secret keys"

        if response.status_code == 200:
            return "running"

        return "unknown"

    except requests.exceptions.SSLError:
        return "initializing"
