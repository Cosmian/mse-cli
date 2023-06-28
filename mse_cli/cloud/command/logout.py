"""mse_cli.cloud.command.logout module."""

import os

import requests

from mse_cli import MSE_AUTH0_DOMAIN_NAME
from mse_cli.cloud.model.user import UserConf
from mse_cli.error import UnexpectedResponse
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("logout", help="log out the current user")

    parser.set_defaults(func=run)


def run(_args) -> None:
    """Run the subcommand."""
    logout()
    LOG.success("You are now logged out.")  # type: ignore


def logout() -> None:
    """Log out the user."""
    r = requests.post(url=f"{MSE_AUTH0_DOMAIN_NAME}/logout?federated", timeout=60)

    if not r.ok:
        raise UnexpectedResponse(r.text)

    login_file = UserConf.path()
    if login_file.exists():
        os.remove(login_file)
