"""Remove subparser definition."""

import uuid

import requests

from mse_ctl.api.app import remove
from mse_ctl.conf.context import Context
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "remove", help="Stop and remove the MSE app from the project")

    parser.set_defaults(func=run)

    parser.add_argument('id', type=uuid.UUID, help='The id of the MSE app.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info("Removing your application from the project...")

    r: requests.Response = remove(conn=user_conf.get_connection(), uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    # Remove the context file
    Context.clean(args.id, ignore_errors=True)
