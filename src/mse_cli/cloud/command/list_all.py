"""mse_cli.cloud.command.list_all module."""

import requests

from mse_cli.cloud.api.project import list_apps
from mse_cli.cloud.api.types import AppStatus, PartialApp
from mse_cli.cloud.command.helpers import get_project_from_name, non_empty_string
from mse_cli.cloud.model.user import UserConf
from mse_cli.color import COLOR, ColorKind
from mse_cli.error import BadApplicationInput, UnexpectedResponse
from mse_cli.log import LOGGER as LOG


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
    user_conf = UserConf.load()
    conn = user_conf.get_connection()

    project_id = None
    if args.project_name:
        project = get_project_from_name(conn, args.project_name)
        if not project:
            raise BadApplicationInput(f"Project {args.project_name} does not exist")

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
        raise UnexpectedResponse(r.text)

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
