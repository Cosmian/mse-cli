"""mse_cli.command.logs module."""

import uuid

import requests

from mse_cli.api.app import log as get_app_logs
from mse_cli.command.helpers import get_app
from mse_cli.conf.user import UserConf
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "logs", help="logs (last 64kB) of a specific MSE web application"
    )

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_uuid",
        type=uuid.UUID,
        help="identifier of the MSE web application to display logs",
    )


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    LOG.info("Fetching the logs (last 64kB) for %s...", args.app_uuid)

    conn = user_conf.get_connection()
    app = get_app(conn=conn, uuid=args.app_uuid)

    r: requests.Response = get_app_logs(conn=conn, uuid=app.uuid)
    if not r.ok:
        raise Exception(r.text)

    logs = r.json()
    LOG.info("")
    LOG.info(logs["stdout"])
