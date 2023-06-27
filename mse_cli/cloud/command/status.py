"""mse_cli.cloud.command.status module."""

import uuid
from datetime import datetime

from mse_cli.cloud.api.types import AppStatus
from mse_cli.cloud.command.helpers import get_app, get_enclave_resources, get_metrics
from mse_cli.cloud.model.user import UserConf
from mse_cli.color import COLOR, ColorKind
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "status", help="status of a specific MSE web application"
    )

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_id",
        type=uuid.UUID,
        help="identifier of the MSE web application to display status",
    )


# pylint: disable=too-many-statements,too-many-branches
def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.load()

    LOG.info("Fetching the app status for %s...", args.app_id)

    conn = user_conf.get_connection()
    app = get_app(conn=conn, app_id=args.app_id)

    (enclave_size, cores) = get_enclave_resources(conn, app.hardware_name)

    # Determine once for all the timezone and use it everywhere later
    tzinfo = app.created_at.astimezone().tzinfo

    LOG.info("\n> Microservice")
    LOG.info("\tName        = %s", app.name)
    LOG.info("\tDomain name = %s", app.domain_name)
    LOG.info("\tHardware    = %s", app.hardware_name)
    LOG.info("\tApplication = %s", app.python_application)
    LOG.info("\tMSE docker  = %s", app.docker)
    LOG.info("\tHealthcheck = %s", app.healthcheck_endpoint)

    LOG.info("\n> Deployment status")
    LOG.info("\tUUID               = %s", app.id)
    LOG.info("\tCertificate origin = %s", app.ssl_certificate_origin.value)
    LOG.info("\tMemory size        = %sM", enclave_size)
    LOG.info("\tCores amount       = %s", cores)
    LOG.info("\tCreated at         = %s", app.created_at.astimezone(tzinfo))

    # Note: date is printed in the current local timezone (instead of utc)
    expires_at = app.expires_at.astimezone(tzinfo)
    remaining_days = expires_at - datetime.now(tzinfo)
    if 0 <= remaining_days.days <= 1:
        remaining_hours = remaining_days.seconds // 3600
        remaining_minutes = remaining_days.seconds % 3600 // 60

        LOG.info(
            "\tExpires at         = %s (%s%s%s%d seconds remaining%s)",
            expires_at,
            COLOR.render(ColorKind.WARNING),
            f"{remaining_hours} hours, " if remaining_hours > 0 else "",
            f"{remaining_minutes} minutes, " if remaining_minutes > 0 else "",
            remaining_days.seconds % 60,
            COLOR.render(ColorKind.ENDC),
        )
    elif remaining_days.days > 1:
        LOG.info(
            "\tExpires at         = %s (%s%d days remaining%s)",
            expires_at,
            COLOR.render(ColorKind.WARNING),
            remaining_days.days,
            COLOR.render(ColorKind.ENDC),
        )
    else:  # expired
        LOG.info(
            "\tExpired at         = %s (%s%d days remaining%s)",
            expires_at,
            COLOR.render(ColorKind.WARNING),
            remaining_days.days,
            COLOR.render(ColorKind.ENDC),
        )

    if app.status == AppStatus.Running:
        LOG.info(
            "\tStatus             = %s%s%s",
            COLOR.render(ColorKind.OKGREEN),
            app.status.value,
            COLOR.render(ColorKind.ENDC),
        )
        if app.ready_at:
            LOG.info("\tOnline since       = %s", app.ready_at.astimezone(tzinfo))
    elif app.status == AppStatus.Stopped:
        LOG.info(
            "\tStatus             = %s%s%s",
            COLOR.render(ColorKind.WARNING),
            app.status.value,
            COLOR.render(ColorKind.ENDC),
        )
        if app.stopped_at:
            LOG.info("\tStopped since      = %s", app.stopped_at.astimezone(tzinfo))
    elif app.status == AppStatus.OnError:
        LOG.info(
            "\tStatus             = %s%s%s",
            COLOR.render(ColorKind.FAIL),
            app.status.value,
            COLOR.render(ColorKind.ENDC),
        )
        if app.stopped_at:
            LOG.info("\tOn error since     = %s", app.stopped_at.astimezone(tzinfo))
    elif app.status in (AppStatus.Initializing, AppStatus.Spawning):
        LOG.info(
            "\tStatus             = %s%s%s",
            COLOR.render(ColorKind.OKBLUE),
            app.status.value,
            COLOR.render(ColorKind.ENDC),
        )

    if app.status == AppStatus.Running:
        metrics = get_metrics(conn=conn, app_id=args.app_id)

        LOG.info("\n> Current metrics")
        if metric := metrics.get("average_queue_time"):
            LOG.info(
                "\tAverage queue time    = %.3fs",
                float(metric[1]),
            )
        if metric := metrics.get("average_connect_time"):
            LOG.info(
                "\tAverage connect time  = %.3fs",
                float(metric[1]),
            )
        if metric := metrics.get("average_response_time"):
            LOG.info(
                "\tAverage response time = %.3fs",
                float(metric[1]),
            )
        if metric := metrics.get(
            "average_query_time",
        ):
            LOG.info(
                "\tAverage query time    = %.3fs",
                float(metric[1]),
            )
        if metric := metrics.get("amount_of_connection"):
            LOG.info(
                "\tAmount of connection  = %d",
                int(metric[1]),
            )
        if metric := metrics.get("cpu_usage"):
            LOG.info("\tCPU usage             = %.2f%%", float(metric[1]))
        if metric := metrics.get("fs_usage"):
            LOG.info("\tFS usage              = %s", sizeof_fmt(int(metric[1])))
        if metric := metrics.get("throughput_in"):
            LOG.info(
                "\tInput throughput      = %s",
                sizeof_fmt(int(metric[1])),
            )
        if metric := metrics.get("throughput_out"):
            LOG.info(
                "\tOutput throughput     = %s",
                sizeof_fmt(int(metric[1])),
            )


def sizeof_fmt(num: int) -> str:
    """Make the size human readable."""
    suffix = "B"
    fnum = float(num)
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(fnum) < 1024.0:
            return f"{fnum:3.1f}{unit}{suffix}"
        fnum /= 1024.0
    return f"{fnum:.1f}Yi{suffix}"
