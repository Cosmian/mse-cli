"""List subparser definition."""

import uuid

import requests

from mse_ctl.api.project import list_apps
from mse_ctl.api.types import App, AppStatus, Project
from mse_ctl.cli.helpers import get_project_from_name
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("list",
                                   help="Print the list of apps from a project")

    parser.set_defaults(func=run)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--id',
                       type=uuid.UUID,
                       help='The id of the MSE project.')

    group.add_argument('--name', type=str, help='The name of the MSE project.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    conn = user_conf.get_connection()

    if args.name:
        project = get_project_from_name(conn, args.name)
        if not project:
            raise Exception(f"Project {args.name} does not exist")
        project_uuid = project.uuid
    else:
        project_uuid = args.id

    log.info("Fetching the project %s...", project_uuid)

    r: requests.Response = list_apps(conn=conn, project_uuid=project_uuid)

    log.info(f"\n%s | %s | %12s | %s ", "App UUID".center(36),
             "Creation date".center(32), "Status".center(12),
             "App summary".center(36))
    log.info(("-" * 126))

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    list_app = r.json()
    for app in list_app:
        app = App.from_json_dict(app)

        color = bcolors.OKGREEN
        if app.status == AppStatus.Stopped:
            color = bcolors.WARNING
        elif app.status == AppStatus.OnError:
            color = bcolors.FAIL
        elif app.status == AppStatus.Initializing:
            color = bcolors.OKBLUE

        log.info(f"%s | %s |%s %s %s| %s %s %s", app.uuid, app.created_at,
                 color, app.status.value.center(12), bcolors.ENDC, app.name,
                 app.version, app.domain_name)
