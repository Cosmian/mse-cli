"""mse_cli.main module."""

import argparse
import os
import sys
import traceback
from warnings import filterwarnings  # noqa: E402

filterwarnings("ignore")  # noqa: E402

# pylint: disable=wrong-import-position
import mse_cli
from mse_cli.cloud.command import context as cloud_context
from mse_cli.cloud.command import deploy as cloud_deploy
from mse_cli.cloud.command import init as cloud_init
from mse_cli.cloud.command import list_all as cloud_list_all
from mse_cli.cloud.command import localtest as cloud_localtest
from mse_cli.cloud.command import login as cloud_login
from mse_cli.cloud.command import logout as cloud_logout
from mse_cli.cloud.command import logs as cloud_logs
from mse_cli.cloud.command import scaffold as cloud_scaffold
from mse_cli.cloud.command import status as cloud_status
from mse_cli.cloud.command import stop as cloud_stop
from mse_cli.cloud.command import test as cloud_test
from mse_cli.cloud.command import verify as cloud_verify
from mse_cli.color import setup_color
from mse_cli.home.command.code_provider import decrypt as home_decrypt
from mse_cli.home.command.code_provider import localtest as home_localtest
from mse_cli.home.command.code_provider import package as home_package
from mse_cli.home.command.code_provider import scaffold as home_scaffold
from mse_cli.home.command.code_provider import seal as home_seal
from mse_cli.home.command.code_provider import verify as home_verify
from mse_cli.home.command.sgx_operator import evidence as home_evidence
from mse_cli.home.command.sgx_operator import list_all as home_list_all
from mse_cli.home.command.sgx_operator import logs as home_logs
from mse_cli.home.command.sgx_operator import restart as home_restart
from mse_cli.home.command.sgx_operator import run as home_run
from mse_cli.home.command.sgx_operator import spawn as home_spawn
from mse_cli.home.command.sgx_operator import status as home_status
from mse_cli.home.command.sgx_operator import stop as home_stop
from mse_cli.home.command.sgx_operator import test as home_test
from mse_cli.log import LOGGER as LOG
from mse_cli.log import setup_logging


# pylint: disable=too-many-statements
def main() -> int:
    """Entrypoint of the CLI."""
    parser = argparse.ArgumentParser(
        description="Microservice Encryption CLI" f" - {mse_cli.__version__}"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{mse_cli.__version__}",
        help="version of %(prog)s binary",
    )

    parser.add_argument(
        "--color",
        default="always",
        choices=["never", "always"],
        help="enable (default) or disable colors on stdout/stderr",
    )

    subparsers = parser.add_subparsers(title="infrastructure")

    parser_cloud = subparsers.add_parser(
        "cloud", help="use Cosmain MSE Cloud infrastructure"
    )
    parser_home = subparsers.add_parser("home", help="use your own SGX infrastructure")

    subparsers_cloud = parser_cloud.add_subparsers(title="operations")
    subparsers_home = parser_home.add_subparsers(title="operations")

    cloud_context.add_subparser(subparsers_cloud)
    cloud_deploy.add_subparser(subparsers_cloud)
    cloud_init.add_subparser(subparsers_cloud)
    cloud_list_all.add_subparser(subparsers_cloud)
    cloud_login.add_subparser(subparsers_cloud)
    cloud_logout.add_subparser(subparsers_cloud)
    cloud_logs.add_subparser(subparsers_cloud)
    cloud_scaffold.add_subparser(subparsers_cloud)
    cloud_status.add_subparser(subparsers_cloud)
    cloud_stop.add_subparser(subparsers_cloud)
    cloud_test.add_subparser(subparsers_cloud)
    cloud_localtest.add_subparser(subparsers_cloud)
    cloud_verify.add_subparser(subparsers_cloud)

    home_decrypt.add_subparser(subparsers_home)
    home_evidence.add_subparser(subparsers_home)
    home_scaffold.add_subparser(subparsers_home)
    home_list_all.add_subparser(subparsers_home)
    home_logs.add_subparser(subparsers_home)
    home_package.add_subparser(subparsers_home)
    home_restart.add_subparser(subparsers_home)
    home_run.add_subparser(subparsers_home)
    home_status.add_subparser(subparsers_home)
    home_seal.add_subparser(subparsers_home)
    home_spawn.add_subparser(subparsers_home)
    home_stop.add_subparser(subparsers_home)
    home_test.add_subparser(subparsers_home)
    home_localtest.add_subparser(subparsers_home)
    home_verify.add_subparser(subparsers_home)

    # We infer the targeted env if the user
    # doesn't specify it in the command
    if default_env := os.getenv("MSE_DEFAULT_ENV"):
        if sys.argv[1] not in ["cloud", "home"]:
            sys.argv.insert(1, default_env)

    args = parser.parse_args()

    setup_color(args.color == "always")
    setup_logging(False)

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")

    try:
        func(args)
        return 0
    # pylint: disable=broad-except
    except Exception as e:
        if os.getenv("MSE_BACKTRACE") == "full":
            traceback.print_exc()

        LOG.error(e)
        return 1


if __name__ == "__main__":
    main()
