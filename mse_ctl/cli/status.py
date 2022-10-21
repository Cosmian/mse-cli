"""Status subparser definition."""

import uuid

import requests

from mse_ctl.api.app import get
from mse_ctl.api.types import App, AppStatus
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("status",
                                   help="Print the status of a MSE app")

    parser.set_defaults(func=run)

    parser.add_argument('--id',
                        required=True,
                        type=uuid.UUID,
                        help='The id of the MSE app.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info("Fetching the app status for %s...", args.id)

    r: requests.Response = get(conn=user_conf.get_connection(), uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    app = App.from_json_dict(r.json())

    log.info("\nMicroservice")
    log.info("\tName        = %s", app.name)
    log.info("\tVersion     = %s", app.version)
    log.info("\tDomain name = %s", app.domain_name)
    log.info("\tLifetime    = %s", app.enclave_lifetime)
    log.info("\tApplication = %s", app.python_application)
    log.info("\tHealthcheck = %s", app.health_check_endpoint)

    log.info("\nDeployement status")
    log.info("\tUUID            = %s", app.uuid)
    log.info("\tSGX MSE lib     = %s", app.enclave_version)
    log.info("\tEnclave size    = %s", app.enclave_size.value)
    log.info("\tCode protection = %s", app.code_protection.value)
    log.info("\tCreated at      = %s", app.created_at)

    if app.status == AppStatus.Running:
        log.info("\tStatus          = %s%s%s", bcolors.OKGREEN,
                 app.status.value, bcolors.ENDC)
        log.info("\tOnline since    = %s", app.ready_at)
    elif app.status == AppStatus.Stopped:
        log.info("\tStatus          = %s%s%s", bcolors.WARNING,
                 app.status.value, bcolors.ENDC)
        log.info("\tStopped since   = %s", app.stopped_at)
    elif app.status == AppStatus.OnError:
        log.info("\tStatus          = %s%s%s", bcolors.FAIL, app.status.value,
                 bcolors.ENDC)
        log.info("\tOn error since  = %s", app.onerror_at)
    elif app.status == AppStatus.Initializing:
        log.info("\tStatus          = %s%s%s", bcolors.OKBLUE, app.status.value,
                 bcolors.ENDC)
