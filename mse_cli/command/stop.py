"""mse_cli.command.stop module.."""

import uuid

from mse_cli.command.helpers import stop_app
from mse_cli.conf.user import UserConf
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.spinner import Spinner


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("stop", help="stop a specific MSE web application")

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_uuid", type=uuid.UUID, help="identifier of the MSE web application to stop"
    )


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    with Spinner("Stopping and destroying the app... "):
        stop_app(user_conf.get_connection(), args.app_uuid)

    LOG.success("App gracefully stopped")  # type: ignore
