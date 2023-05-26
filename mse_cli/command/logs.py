"""mse_cli.command.logs module."""

import uuid

import requests

from mse_cli.api.app import log as get_app_logs
from mse_cli.command.helpers import get_app
from mse_cli.log import LOGGER as LOG
from mse_cli.model.user import UserConf


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "logs", help="logs (last 64kB) of a specific MSE web application"
    )

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_id",
        type=uuid.UUID,
        help="identifier of the MSE web application to display logs",
    )


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    LOG.info("Fetching the logs (last 64kB) for %s...", args.app_id)

    conn = user_conf.get_connection()
    app = get_app(conn=conn, app_id=args.app_id)

    r: requests.Response = get_app_logs(conn=conn, app_id=app.id)
    if not r.ok:
        raise Exception(r.text)

    logs = r.json()
    LOG.info("")
    LOG.info(logs["stdout"])
