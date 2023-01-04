"""mse_ctl.cli.status module."""

import uuid
from datetime import datetime, timezone

import requests

from mse_ctl.api.app import log as get_app_logs
from mse_ctl.api.types import AppStatus
from mse_ctl.cli.helpers import get_app, get_enclave_resources
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as LOG
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "status", help="status of a specific MSE web application")

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_uuid",
        type=uuid.UUID,
        help="identifier of the MSE web application to display status")
    parser.add_argument("--log",
                        action="store_true",
                        help="output log of the MSE web application")


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    LOG.info("Fetching the app status for %s...", args.app_uuid)

    conn = user_conf.get_connection()
    app = get_app(conn=conn, uuid=args.app_uuid)

    (enclave_size, cores) = get_enclave_resources(conn, app.plan)

    LOG.info("\n> Microservice")
    LOG.info("\tName         = %s", app.name)
    LOG.info("\tVersion      = %s", app.version)
    LOG.info("\tDomain name  = %s", app.domain_name)
    LOG.info("\tBilling plan = %s", app.plan)
    LOG.info("\tApplication  = %s", app.python_application)
    LOG.info("\tMSE docker   = %s", app.docker)
    LOG.info("\tHealthcheck  = %s", app.health_check_endpoint)

    LOG.info("\n> Deployement status")
    LOG.info("\tUUID               = %s", app.uuid)
    LOG.info("\tCertificate origin = %s", app.ssl_certificate_origin.value)
    LOG.info("\tEnclave size       = %sM", enclave_size)
    LOG.info("\tCores amount       = %s", cores)
    LOG.info("\tCreated at         = %s", app.created_at.astimezone())

    # Note: we print the date in the current local timezone (instead of utc)
    remaining_days = app.expires_at - datetime.now(timezone.utc)
    if 0 <= remaining_days.days <= 1:
        LOG.info("\tExpires at         = %s (%s%d secondes remaining%s)",
                 app.expires_at.astimezone(), bcolors.WARNING,
                 remaining_days.seconds, bcolors.ENDC)
    elif remaining_days.days > 1:
        LOG.info("\tExpires at         = %s (%s%d days remaining%s)",
                 app.expires_at.astimezone(), bcolors.WARNING,
                 remaining_days.days, bcolors.ENDC)
    else:
        LOG.info("\tExpired at         = %s (%s%d days remaining%s)",
                 app.expires_at.astimezone(), bcolors.WARNING,
                 remaining_days.days, bcolors.ENDC)

    if app.status == AppStatus.Running:
        LOG.info("\tStatus             = %s%s%s", bcolors.OKGREEN,
                 app.status.value, bcolors.ENDC)
        if app.ready_at:
            LOG.info("\tOnline since       = %s", app.ready_at.astimezone())
    elif app.status == AppStatus.Stopped:
        LOG.info("\tStatus             = %s%s%s", bcolors.WARNING,
                 app.status.value, bcolors.ENDC)
        if app.stopped_at:
            LOG.info("\tStopped since      = %s", app.stopped_at.astimezone())
    elif app.status == AppStatus.OnError:
        LOG.info("\tStatus             = %s%s%s", bcolors.FAIL,
                 app.status.value, bcolors.ENDC)
        if app.onerror_at:
            LOG.info("\tOn error since     = %s", app.onerror_at.astimezone())
    elif app.status in (AppStatus.Initializing, AppStatus.Spawning):
        LOG.info("\tStatus             = %s%s%s", bcolors.OKBLUE,
                 app.status.value, bcolors.ENDC)

    if args.log and app.status != AppStatus.Deleted:
        r: requests.Response = get_app_logs(conn=conn, uuid=app.uuid)
        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        logs = r.json()
        LOG.info("\n> Stdout")
        LOG.info(logs["stdout"])
