"""mse_cli.command.list_all module."""

import requests

from mse_cli.api.project import list_apps
from mse_cli.api.types import AppStatus, PartialApp
from mse_cli.command.helpers import get_project_from_name, non_empty_string
from mse_cli.conf.user import UserConf
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.color import COLOR, ColorKind


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "list", help="list deployed MSE web application from a project"
    )

    parser.set_defaults(func=run)

    parser.add_argument(
        "project_name",
        nargs="?",
        type=non_empty_string,
        help="name of the project to consider when displaying the apps list",
    )

    parser.add_argument("--all", action="store_true", help="also list the stopped apps")


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    conn = user_conf.get_connection()

    project_id = None
    if args.project_name:
        project = get_project_from_name(conn, args.project_name)
        if not project:
            raise Exception(f"Project {args.project_name} does not exist")

        LOG.info("Fetching the apps in project %s...", project.name)
        project_id = project.id
    else:
        LOG.info("Fetching the apps in all projects...")

    status = None
    if not args.all:
        status = [
            AppStatus.Spawning,
            AppStatus.Initializing,
            AppStatus.Running,
        ]

    r: requests.Response = list_apps(conn=conn, project_id=project_id, status=status)

    if not r.ok:
        raise Exception(r.text)

    LOG.info(
        "\n%s | %s | %12s | %s ",
        "App UUID".center(36),
        "Creation date".center(32),
        "Status".center(12),
        "App summary".center(36),
    )
    LOG.info(("-" * 126))

    list_app = r.json()
    for app in list_app:
        app = PartialApp.from_dict(app)

        color = COLOR.render(ColorKind.OKGREEN)
        if app.status == AppStatus.Stopped:
            color = COLOR.render(ColorKind.WARNING)
        elif app.status == AppStatus.OnError:
            color = COLOR.render(ColorKind.FAIL)
        elif app.status == AppStatus.Initializing:
            color = COLOR.render(ColorKind.OKBLUE)
        elif app.status == AppStatus.Spawning:
            color = COLOR.render(ColorKind.OKBLUE)

        LOG.info(
            "%s | %s |%s %s %s| %s on %s%s%s",
            app.id,
            app.created_at.astimezone(),
            color,
            app.status.value.center(12),
            COLOR.render(ColorKind.ENDC),
            app.name,
            COLOR.render(ColorKind.OKBLUE),
            app.domain_name,
            COLOR.render(ColorKind.ENDC),
        )
