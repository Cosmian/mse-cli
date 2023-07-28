"""mse_cli.cloud.command.localtest module.."""

import uuid
from pathlib import Path

from docker.errors import ImageNotFound

from mse_cli.cloud.command.helpers import get_client_docker
from mse_cli.common.helpers import try_run_test_docker
from mse_cli.core.conf import AppConf
from mse_cli.core.test_docker import TestDockerConfig
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "localtest", help="test locally the application in the MSE docker"
    )

    parser.add_argument(
        "--path",
        type=Path,
        required=False,
        metavar="FILE",
        help="path to the MSE app to test (current directory if not set)",
    )

    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="do not run the tests: just start the docker",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    app = AppConf.load(path=args.path)
    cloud_conf = app.cloud_or_raise()
    client = get_client_docker()

    LOG.info("Starting the docker: %s...", cloud_conf.docker)

    # Pull always before running.
    # If image is not found: let's assume it's a local image
    try:
        client.images.pull(cloud_conf.docker)
    except ImageNotFound:
        pass

    docker_config = TestDockerConfig(
        code=cloud_conf.code,
        application=app.python_application,
        secrets=cloud_conf.secrets,
        sealed_secrets=None,
        port=5000,
    )

    try_run_test_docker(
        app,
        client,
        cloud_conf.docker,
        str(uuid.uuid4()),
        docker_config,
        cloud_conf.tests,
        None,
        None,
        args.no_tests,
    )
