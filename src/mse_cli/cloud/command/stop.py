"""mse_cli.cloud.command.stop module.."""

import uuid

from mse_cli.cloud.command.helpers import stop_app
from mse_cli.cloud.model.user import UserConf
from mse_cli.core.spinner import Spinner
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("stop", help="stop a specific MSE web application")

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_id",
        type=uuid.UUID,
        nargs="+",
        help="identifier of the MSE web application to stop",
    )


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.load()

    for app_id in args.app_id:
        with Spinner(f"Stopping and destroying the app {app_id}... "):
            stop_app(user_conf.get_connection(), app_id)

        LOG.success("App gracefully stopped")  # type: ignore
