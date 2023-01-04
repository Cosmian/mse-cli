"""mse_ctl.cli.init module."""

import os
from pathlib import Path

from mse_ctl import MSE_DEFAULT_DOCKER
from mse_ctl.conf.app import AppConf, CodeConf
from mse_ctl.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("init",
                                   help="create a new configuration file in "
                                   "the current directory")

    parser.set_defaults(func=run)


def run(_args):
    """Run the subcommand."""
    LOG.info("We need you to fill in the following fields\n")

    app_name = input("App name: ")
    app_version = input("App version: ")
    project_name = input("Project name [default]: ") or "default"
    plan = input("Plan id [free]: ") or "free"
    dev_input = input("Enable dev mode (yes/[no]): ")
    dev = dev_input.lower() in ["y", "yes"]
    docker = input(f"Docker url [{MSE_DEFAULT_DOCKER}]: ") or MSE_DEFAULT_DOCKER
    code_location = input("Code location [.]:") or "."
    python_application = input("Python application [app:app]: ") or "app:app"
    health_check_endpoint = input("Health check endpoint [/]: ") or "/"

    app = AppConf(name=app_name,
                  version=app_version,
                  project=project_name,
                  plan=plan,
                  dev=dev,
                  code=CodeConf(location=code_location,
                                python_application=python_application,
                                health_check_endpoint=health_check_endpoint,
                                docker=docker))

    path = Path(os.getcwd())
    app.save(path)
    LOG.info("Your app configuration has been saved in: %s", path / "mse.toml")
