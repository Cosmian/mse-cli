"""mse_cli.command.list_all module."""

import requests

from mse_cli.api.project import list_apps
from mse_cli.api.types import App, AppStatus
from mse_cli.command.helpers import get_project_from_name, non_empty_string
from mse_cli.conf.user import UserConf
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "list", help="list deployed MSE web application from a project")

    parser.set_defaults(func=run)

    parser.add_argument(
        "project_name",
        type=non_empty_string,
        help="name of the project with MSE applications to list")


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    conn = user_conf.get_connection()

    project = get_project_from_name(conn, args.project_name)
    if not project:
        raise Exception(f"Project {args.project_name} does not exist")

    LOG.info("Fetching the project %s...", project.uuid)

    r: requests.Response = list_apps(conn=conn,
                                     project_uuid=project.uuid,
                                     status=[
                                         AppStatus.Spawning,
                                         AppStatus.Initializing,
                                         AppStatus.Running, AppStatus.OnError
                                     ])

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    LOG.info("\n%s | %s | %12s | %s ", "App UUID".center(36),
             "Creation date".center(32), "Status".center(12),
             "App summary".center(36))
    LOG.info(("-" * 126))

    list_app = r.json()
    for app in list_app:
        app = App.from_dict(app)

        color = bcolors.OKGREEN
        if app.status == AppStatus.Stopped:
            color = bcolors.WARNING
        elif app.status == AppStatus.OnError:
            color = bcolors.FAIL
        elif app.status == AppStatus.Initializing:
            color = bcolors.OKBLUE
        elif app.status == AppStatus.Spawning:
            color = bcolors.OKBLUE

        LOG.info("%s | %s |%s %s %s| %s-%s on %s%s%s", app.uuid,
                 app.created_at.astimezone(), color,
                 app.status.value.center(12), bcolors.ENDC, app.name,
                 app.version, bcolors.OKBLUE, app.domain_name, bcolors.ENDC)
