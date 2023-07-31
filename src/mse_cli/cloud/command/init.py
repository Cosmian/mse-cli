"""mse_cli.cloud.command.init module."""

import os
from pathlib import Path

from mse_cli.cloud.command.helpers import get_default
from mse_cli.cloud.model.user import UserConf
from mse_cli.core.conf import AppConf, CloudConf
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "init", help="create a new configuration file in " "the current directory"
    )

    parser.set_defaults(func=run)


def run(_args) -> None:
    """Run the subcommand."""
    LOG.info("We need you to fill in the following fields\n")
    user_conf = UserConf.load()
    conn = user_conf.get_connection()

    config = get_default(conn=conn)

    app_name = input("App name: ")
    project_name = input(f"Project name [{config.project}]: ") or config.project
    hardware = input(f"Hardware name [{config.hardware}]: ") or config.hardware
    docker = input(f"Docker url [{config.docker}]: ") or config.docker
    code_location = input("Code location [mse_src]:") or "mse_src"
    tests_location = input("Tests location [tests]:") or "tests"
    python_application = input("Python application [app:app]: ") or "app:app"
    healthcheck_endpoint = input("Health check endpoint [/]: ") or "/"
    secrets_enable = input("Do you have application secrets to provide [no]: ") or "no"
    secrets = Path("secrets.json") if secrets_enable.lower() in ["y", "yes"] else None

    app = AppConf(
        name=app_name,
        python_application=python_application,
        healthcheck_endpoint=healthcheck_endpoint,
        tests_cmd="pytest",
        tests_requirements=["pytest"],
        cloud=CloudConf(
            code=Path(code_location),
            tests=Path(tests_location),
            project=project_name,
            hardware=hardware,
            docker=docker,
            secrets=secrets,
            expiration_date=None,
        ),
    )

    path = Path(os.getcwd())
    app.save(path / "mse.toml")
    LOG.success(  # type: ignore
        "Your app configuration has been saved in: %s",
        path / "mse.toml",
    )
