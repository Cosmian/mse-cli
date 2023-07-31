"""mse_cli.home.command.sgx_operator.run module."""

import json
from pathlib import Path

from mse_cli.core.bootstrap import (
    ConfigurationPayload,
    configure_app,
    is_waiting_for_secrets,
    wait_for_app_server,
)
from mse_cli.core.clock_tick import ClockTick
from mse_cli.core.sgx_docker import SgxDockerConfig
from mse_cli.core.spinner import Spinner
from mse_cli.error import AppContainerBadState
from mse_cli.home.command.helpers import get_client_docker, get_running_app_container
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "run",
        help="finalise the configuration of the application "
        "docker and run the application code",
    )

    parser.add_argument(
        "name",
        type=str,
        help="name of the application",
    )

    parser.add_argument(
        "--secrets",
        type=Path,
        help="secrets.json file path",
    )

    parser.add_argument(
        "--sealed-secrets",
        type=Path,
        help="sealed secrets.json file path",
    )

    parser.add_argument(
        "--key",
        type=Path,
        help="code decryption sealed key file path",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        required=False,
        default=24 * 60,
        help="stop the deployment if the application does not "
        "respond after a delay (in min). (Default: 1440 min)",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    client = get_client_docker()
    container = get_running_app_container(client, args.name)

    docker = SgxDockerConfig.load(container.attrs, container.labels)

    if not is_waiting_for_secrets(f"https://{docker.host}:{docker.port}", False):
        raise AppContainerBadState(
            "Your application is not waiting for secrets. Have you already set it?"
        )

    data = ConfigurationPayload(
        app_id=docker.app_id,
        secrets=json.loads(args.secrets.read_text()) if args.secrets else None,
        sealed_secrets=args.sealed_secrets.read_bytes()
        if args.sealed_secrets
        else None,
        code_secret_key=args.key.read_bytes() if args.key else None,
        ssl_private_key=None,
    )

    LOG.info("Sending data to the configuration server...")
    configure_app(
        f"https://{docker.host}:{docker.port}",
        data.payload(),
        False,
    )
    LOG.info("Your application is now configured!")

    with Spinner("Waiting for your application to be ready... "):
        wait_for_app_server(
            ClockTick(
                period=5,
                timeout=60 * args.timeout,
                message="Your application is unreachable!",
            ),
            f"https://{docker.host}:{docker.port}",
            docker.healthcheck,
            False,
            get_running_app_container,
            (
                client,
                args.name,
            ),
        )

    LOG.info("Application ready!")
    LOG.info("Feel free to test it using the `mse home test` command")
