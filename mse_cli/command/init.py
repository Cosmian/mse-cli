"""mse_cli.command.init module."""

import os
from pathlib import Path

from mse_cli import MSE_DEFAULT_DOCKER
from mse_cli.conf.app import AppConf, CodeConf
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "init", help="create a new configuration file in " "the current directory"
    )

    parser.set_defaults(func=run)


def run(_args):
    """Run the subcommand."""
    LOG.info("We need you to fill in the following fields\n")

    app_name = input("App name: ")
    project_name = input("Project name [default]: ") or "default"
    resource = input("Resource name [free]: ") or "free"
    docker = input(f"Docker url [{MSE_DEFAULT_DOCKER}]: ") or MSE_DEFAULT_DOCKER
    code_location = input("Code location [.]:") or "."
    python_application = input("Python application [app:app]: ") or "app:app"
    healthcheck_endpoint = input("Health check endpoint [/]: ") or "/"
    secrets_enable = input("Do you have application secrets to provide [no]: ") or "no"
    secrets = "secrets.json" if secrets_enable.lower() in ["y", "yes"] else None

    app = AppConf(
        name=app_name,
        project=project_name,
        resource=resource,
        code=CodeConf(
            location=code_location,
            python_application=python_application,
            healthcheck_endpoint=healthcheck_endpoint,
            docker=docker,
            secrets=secrets,
        ),
    )

    path = Path(os.getcwd())
    app.save(path)
    LOG.success("Your app configuration has been saved in: %s", path / "mse.toml")
