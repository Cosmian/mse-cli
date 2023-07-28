"""mse_cli.home.command.sgx_operator.test module."""

import os
import subprocess
import sys
from pathlib import Path

from mse_cli.core.bootstrap import is_waiting_for_secrets
from mse_cli.core.conf import AppConf, AppConfParsingOption
from mse_cli.core.sgx_docker import SgxDockerConfig
from mse_cli.error import AppContainerBadState
from mse_cli.home.command.helpers import get_client_docker, get_running_app_container
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("test", help="Test a deployed MSE app")

    parser.add_argument(
        "name",
        type=str,
        help="the name of the application",
    )

    parser.add_argument(
        "--test",
        type=Path,
        required=True,
        help="the path of the test directory extracted from the MSE package",
    )

    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="the conf path extracted from the MSE package",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    client = get_client_docker()
    container = get_running_app_container(client, args.name)

    docker = SgxDockerConfig.load(container.attrs, container.labels)

    if is_waiting_for_secrets(f"https://{docker.host}:{docker.port}"):
        raise AppContainerBadState(
            "Your application is waiting for secrets and can't be tested right now."
        )

    code_config = AppConf.load(args.config, option=AppConfParsingOption.SkipCloud)

    for package in code_config.tests_requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    try:
        subprocess.check_call(
            code_config.tests_cmd,
            cwd=args.test,
            env=dict(
                os.environ, TEST_REMOTE_URL=f"https://{docker.host}:{docker.port}"
            ),
        )

        LOG.info("Tests successful")
    except subprocess.CalledProcessError:
        LOG.error("Tests failed!")
