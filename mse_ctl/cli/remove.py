"""mse_ctl.cli.remove module."""

import uuid

import requests

from mse_ctl.api.app import remove
from mse_ctl.conf.context import Context
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as LOG
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "remove", help="stop and remove a specific MSE web application")

    parser.set_defaults(func=run)

    parser.add_argument("uuid",
                        type=uuid.UUID,
                        help="identifier of the MSE web application to remove")


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    LOG.info("Removing your application from the project...")

    r: requests.Response = remove(conn=user_conf.get_connection(),
                                  uuid=args.uuid)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    # Remove the context file
    Context.clean(args.uuid, ignore_errors=True)

    LOG.info("%sApplication successfully removed%s", bcolors.OKGREEN,
             bcolors.ENDC)
