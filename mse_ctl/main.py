"""mse_ctl.main module."""

import argparse
from warnings import filterwarnings

import mse_ctl
from mse_ctl.cli import (context, deploy, init, list_all, login, logout, remove,
                         scaffold, status, stop, test, verify)
from mse_ctl.log import setup_logging

filterwarnings("ignore")


def main() -> int:
    """Entrypoint of the CLI."""
    setup_logging(False)

    parser = argparse.ArgumentParser(
        description="MicroService Encryption control CLI"
        f" - {mse_ctl.__version__}")

    parser.add_argument("--version",
                        action="version",
                        version=f"{mse_ctl.__version__}",
                        help="version of %(prog)s binary")

    subparsers = parser.add_subparsers(title="subcommands")

    context.add_subparser(subparsers)
    deploy.add_subparser(subparsers)
    init.add_subparser(subparsers)
    list_all.add_subparser(subparsers)
    login.add_subparser(subparsers)
    logout.add_subparser(subparsers)
    remove.add_subparser(subparsers)
    scaffold.add_subparser(subparsers)
    status.add_subparser(subparsers)
    stop.add_subparser(subparsers)
    test.add_subparser(subparsers)
    verify.add_subparser(subparsers)

    args = parser.parse_args()

    args.func(args)

    return 0


if __name__ == "__main__":
    main()
