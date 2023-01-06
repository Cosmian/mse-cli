"""Test subparser definition."""

from pathlib import Path

import docker

from mse_cli.conf.app import AppConf
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "test", help="Test locally the application in the mse docker")

    parser.add_argument(
        '--path',
        type=Path,
        required=False,
        metavar='FILE',
        help='Path to the mse app to test (current directory if not set)')

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    app = AppConf.from_toml(path=args.path)

    LOG.info("Starting the docker: %s...", app.code.docker)

    client = docker.from_env()

    # Pull always before running (not for local docker)
    if "/" not in app.code.docker:
        client.images.pull(app.code.docker)

    LOG.info("You can stop the test at any time typing CTRL^C")
    LOG.info(
        "%sFrom another terminal, you can now run: "
        "`curl http://localhost:5000%s` or `pytest`%s", bcolors.OKBLUE,
        app.code.health_check_endpoint, bcolors.ENDC)

    command = ["--application", app.code.python_application, "--debug"]

    volumes = {f"{app.code.location}": {'bind': '/app/code', 'mode': 'rw'}}

    container = client.containers.run(
        app.code.docker,
        command=command,
        volumes=volumes,
        entrypoint="mse-test",
        ports={'5000/tcp': 5000},
        remove=True,
        detach=True,
        stdout=True,
        stderr=True,
    )

    try:
        # Print logs until the docker is up
        for line in container.logs(stream=True):
            LOG.info(line.decode('utf-8').strip())
    except KeyboardInterrupt:
        # Stop the docker when user types CTRL^C
        LOG.info("Stopping the docker container...")
        container.stop(timeout=1)
