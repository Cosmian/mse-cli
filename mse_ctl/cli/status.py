"""Status subparser definition."""

import uuid

from datetime import datetime, timezone

import requests

from mse_ctl.api.app import get
from mse_ctl.api.types import App, AppStatus
from mse_ctl.cli.helpers import get_enclave_resources
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("status",
                                   help="Print the status of a MSE app")

    parser.set_defaults(func=run)

    parser.add_argument('id', type=uuid.UUID, help='The id of the MSE app.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info("Fetching the app status for %s...", args.id)

    conn = user_conf.get_connection()
    r: requests.Response = get(conn=conn, uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    app = App.from_json_dict(r.json())

    (enclave_size, cores) = get_enclave_resources(conn, app.plan)

    log.info("\nMicroservice")
    log.info("\tName         = %s", app.name)
    log.info("\tVersion      = %s", app.version)
    log.info("\tDomain name  = %s", app.domain_name)
    log.info("\tBilling plan = %s", app.plan)
    log.info("\tApplication  = %s", app.python_application)
    log.info("\tHealthcheck  = %s", app.health_check_endpoint)

    log.info("\nDeployement status")
    log.info("\tUUID               = %s", app.uuid)
    log.info("\tMSE docker version = %s", app.docker_version)
    log.info("\tCertificate origin = %s", app.ssl_certificate_origin.value)
    log.info("\tEnclave size       = %sM", enclave_size)
    log.info("\tCores amount       = %s", cores)

    log.info("\tCreated at         = %s", app.created_at.astimezone())

    # Note: we print the date in the current local timezone (instead of utc)
    remaining_days = app.expires_at - datetime.now(timezone.utc)
    if remaining_days.days >= 0 and remaining_days.days <= 1:
        log.info("\tExpires at         = %s (%s%d secondes remaining%s)",
                 app.expires_at.astimezone(), bcolors.WARNING,
                 remaining_days.seconds, bcolors.ENDC)
    elif remaining_days.days > 1:
        log.info("\tExpires at         = %s (%s%d days remaining%s)",
                 app.expires_at.astimezone(), bcolors.WARNING,
                 remaining_days.days, bcolors.ENDC)
    else:
        log.info("\tExpired at         = %s (%s%d days remaining%s)",
                 app.expires_at.astimezone(), bcolors.WARNING,
                 remaining_days.days, bcolors.ENDC)

    if app.status == AppStatus.Running:
        log.info("\tStatus             = %s%s%s", bcolors.OKGREEN,
                 app.status.value, bcolors.ENDC)
        log.info("\tOnline since       = %s", app.ready_at.astimezone())
    elif app.status == AppStatus.Stopped:
        log.info("\tStatus             = %s%s%s", bcolors.WARNING,
                 app.status.value, bcolors.ENDC)
        log.info("\tStopped since      = %s", app.stopped_at.astimezone())
    elif app.status == AppStatus.OnError:
        log.info("\tStatus             = %s%s%s", bcolors.FAIL,
                 app.status.value, bcolors.ENDC)
        log.info("\tOn error since     = %s", app.onerror_at.astimezone())
    elif app.status in (AppStatus.Initializing, AppStatus.Spawning):
        log.info("\tStatus             = %s%s%s", bcolors.OKBLUE,
                 app.status.value, bcolors.ENDC)
