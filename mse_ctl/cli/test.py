"""Test subparser definition."""

from pathlib import Path

import docker

from mse_ctl.conf.app import AppConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "test", help="Test locally the application in the mse docker")

    parser.add_argument(
        '--path',
        type=Path,
        required=False,
        metavar='PATH',
        help='Path to the mse app to test (current directory if not set)')

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    app = AppConf.from_toml(path=args.path)

    log.info("Starting the docker: %s...", app.code.docker)

    client = docker.from_env()

    # Pull always before running
    client.images.pull(app.code.docker)

    log.info("You can stop the docker at any times typing CTRL^C")
    log.info("You can now run: `curl http://localhost:5000%s`",
             app.code.health_check_endpoint)

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
            log.info(line.decode('utf-8').strip())
    except KeyboardInterrupt:
        # Stop the docker when user types CTRL^C
        log.info("Stopping the docker container...")
        container.stop(timeout=1)
