"""Test subparser definition."""

from pathlib import Path

from docker.errors import ImageNotFound
from mse_cli_core.conf import AppConf
from mse_cli_core.test_docker import TestDockerConfig

from mse_cli.command.helpers import get_client_docker
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "test", help="Test locally the application in the MSE docker"
    )

    parser.add_argument(
        "--path",
        type=Path,
        required=False,
        metavar="FILE",
        help="Path to the MSE app to test (current directory if not set)",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    app = AppConf.load(path=args.path)
    cloud_conf = app.cloud_or_raise()

    LOG.info("Starting the docker: %s...", cloud_conf.docker)

    client = get_client_docker()

    # Pull always before running.
    # If image is not found: let's assume it's a local image
    try:
        client.images.pull(cloud_conf.docker)
    except ImageNotFound:
        pass

    LOG.info("You can stop the application at any time by typing CTRL+C or CTRL+Break")
    LOG.advice(  # type: ignore
        "Once started, from another terminal, you can run: "
        "\n\n\tcurl http://localhost:5000%s\n\nor:\n\n\tpytest\n",
        app.healthcheck_endpoint,
    )

    docker_config = TestDockerConfig(
        code=cloud_conf.location,
        application=app.python_application,
        secrets=cloud_conf.secrets,
        sealed_secrets=None,
        port=5000,
    )

    container = client.containers.run(
        cloud_conf.docker,
        command=docker_config.cmd(),
        volumes=docker_config.volumes(),
        entrypoint=TestDockerConfig.entrypoint,
        ports=docker_config.ports(),
        remove=True,
        detach=True,
        stdout=True,
        stderr=True,
    )

    try:
        # Print logs until the docker is up
        for line in container.logs(stream=True):
            LOG.info(line.decode("utf-8").strip())
    except KeyboardInterrupt:
        # Stop the docker when user types CTRL^C
        LOG.info("Stopping the docker container...")
        container.stop(timeout=1)
