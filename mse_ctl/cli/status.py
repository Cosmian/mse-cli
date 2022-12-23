"""Status subparser definition."""

import uuid

from datetime import datetime, timezone

import requests

from mse_ctl.api.app import log as get_app_logs
from mse_ctl.api.types import AppStatus
from mse_ctl.cli.helpers import get_app, get_enclave_resources
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("status",
                                   help="Print the status of a MSE app")

    parser.set_defaults(func=run)

    parser.add_argument('app_id', type=uuid.UUID, help='The id of the MSE app.')
    parser.add_argument('--log',
                        action='store_true',
                        help='Print the log of the app.')


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info("Fetching the app status for %s...", args.app_id)

    conn = user_conf.get_connection()
    app = get_app(conn=conn, uuid=args.app_id)

    (enclave_size, cores) = get_enclave_resources(conn, app.plan)

    log.info("\n> Microservice")
    log.info("\tName         = %s", app.name)
    log.info("\tVersion      = %s", app.version)
    log.info("\tDomain name  = %s", app.domain_name)
    log.info("\tBilling plan = %s", app.plan)
    log.info("\tApplication  = %s", app.python_application)
    log.info("\tHealthcheck  = %s", app.health_check_endpoint)

    log.info("\n> Deployement status")
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
        if app.ready_at:
            log.info("\tOnline since       = %s", app.ready_at.astimezone())
    elif app.status == AppStatus.Stopped:
        log.info("\tStatus             = %s%s%s", bcolors.WARNING,
                 app.status.value, bcolors.ENDC)
        if app.stopped_at:
            log.info("\tStopped since      = %s", app.stopped_at.astimezone())
    elif app.status == AppStatus.OnError:
        log.info("\tStatus             = %s%s%s", bcolors.FAIL,
                 app.status.value, bcolors.ENDC)
        if app.onerror_at:
            log.info("\tOn error since     = %s", app.onerror_at.astimezone())
    elif app.status in (AppStatus.Initializing, AppStatus.Spawning):
        log.info("\tStatus             = %s%s%s", bcolors.OKBLUE,
                 app.status.value, bcolors.ENDC)

    if args.log and app.status != AppStatus.Deleted:
        r: requests.Response = get_app_logs(conn=conn, uuid=app.uuid)
        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        logs = r.json()
        log.info("\n> Stdout")
        log.info(logs["stdout"])
