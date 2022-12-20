"""Test subparser definition."""

from pathlib import Path

import docker

from mse_ctl import MSE_DOCKER_IMAGE_URL
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
        metavar='path/to/mse/app/mse.toml',
        help='Path to the mse app to test (current directory if not set)')

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    app_conf = AppConf.from_toml(path=args.path)

    log.info("Starting the docker: %s")
    log.info("You can run: `curl http://localhost:5000/`")

    run_test(app_conf)


def run_test(app: AppConf):
    """Run the application in the docker."""
    client = docker.from_env()

    image = f"{MSE_DOCKER_IMAGE_URL}:51aee992"  # TODO: get that from app conf

    # Pull always before running
    client.images.pull(image)

    command = ["--application", app.code.python_application, "--debug"]

    volumes = {f"{app.code.location}": {'bind': '/app/code', 'mode': 'rw'}}

    container = client.containers.run(
        image,
        command=command,
        volumes=volumes,
        entrypoint="mse-test",
        ports={'5000/tcp': 5000},
        remove=True,
        detach=False,
        stdout=True,
        stderr=True,
    )

    # Save the docker output
    log.info("%s", container)
