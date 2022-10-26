"""Remove subparser definition."""

import uuid

from mse_ctl.cli.helpers import stop_app
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

    stop_app(user_conf.get_connection(), args.id)
