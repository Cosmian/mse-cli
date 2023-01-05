"""mse_ctl.cli.logout module."""

import os

import requests

from mse_ctl import MSE_AUTH0_DOMAIN_NAME
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("logout", help="log out the current user")

    parser.set_defaults(func=run)


def run(_args) -> None:
    """Run the subcommand."""
    r = requests.post(url=f"{MSE_AUTH0_DOMAIN_NAME}/logout?federated",
                      timeout=60)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    login_file = UserConf.path()
    if login_file.exists():
        os.remove(login_file)

    LOG.info("You are now logged out.")
