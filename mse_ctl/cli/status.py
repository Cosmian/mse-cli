"""Status subparser definition."""

from pathlib import Path
import uuid

import requests
from mse_ctl.api.enclave import get
from mse_ctl.api.types import Enclave

from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("status",
                                   help="Print the status of a MSE enclave ")

    parser.set_defaults(func=run)

    parser.add_argument('--id',
                        required=True,
                        type=uuid.UUID,
                        help='The id of the MSE enclave.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info(f"Fetching the enclave status for {args.id}...")

    r: requests.Response = get(conn=user_conf.get_connection(), uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    enclave = Enclave.from_json_dict(r.json())

    log.info(enclave)
