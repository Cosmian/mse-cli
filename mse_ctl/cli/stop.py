"""Remove subparser definition."""

import uuid

import requests

from mse_ctl.api.app import stop
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("stop", help="Stop a MSE app")

    parser.set_defaults(func=run)

    parser.add_argument('--id',
                        required=True,
                        type=uuid.UUID,
                        help='The id of the MSE app.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info("Stopping and destroying the app...")

    r: requests.Response = stop(conn=user_conf.get_connection(), uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")
