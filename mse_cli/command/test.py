"""Test subparser definition."""

from pathlib import Path

from mse_cli.command.helpers import get_client_docker
from mse_cli.conf.app import AppConf
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
    app = AppConf.from_toml(path=args.path)

    LOG.info("Starting the docker: %s...", app.code.docker)

    client = get_client_docker()

    # Pull always before running (not for local docker)
    if "/" in app.code.docker:
        client.images.pull(app.code.docker)

    LOG.info("You can stop the application at any time by typing CTRL^C")
    LOG.advice(  # type: ignore
        "Once started, from another terminal, you can run: "
        "\n\n\tcurl http://localhost:5000%s\n\nor:\n\n\tpytest\n",
        app.code.healthcheck_endpoint,
    )

    command = ["--application", app.code.python_application, "--debug"]

    volumes = {
        f"{app.code.location}": {"bind": "/mse-app", "mode": "rw"},
    }

    if app.code.secrets:
        volumes[f"{app.code.secrets}"] = {
            "bind": "/root/.cache/mse/secrets.json",
            "mode": "rw",
        }

    container = client.containers.run(
        app.code.docker,
        command=command,
        volumes=volumes,
        entrypoint="mse-test",
        ports={"5000/tcp": ("127.0.0.1", 5000)},
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
