"""Remove subparser definition."""

from pathlib import Path
import uuid

import requests
from mse_ctl.api.enclave import remove
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("remove",
                                   help="Stop and remove a MSE enclave")

    parser.set_defaults(func=run)

    parser.add_argument('--id',
                        required=True,
                        type=uuid.UUID,
                        help='The id of the MSE enclave.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info("Stopping your application and destroying the enclave...")

    r: requests.Response = remove(conn=user_conf.get_connection(), uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")
