"""mse_cli.main module."""

import argparse
from warnings import filterwarnings  # noqa: E402

filterwarnings("ignore")  # noqa: E402

# pylint: disable=wrong-import-position
import mse_cli
from mse_cli.command import (
    context,
    deploy,
    init,
    list_all,
    login,
    logout,
    logs,
    scaffold,
    status,
    stop,
    test,
    verify,
)
from mse_cli.log import setup_logging


def main() -> int:
    """Entrypoint of the CLI."""
    setup_logging(False)

    parser = argparse.ArgumentParser(
        description="MicroService Encryption CLI" f" - {mse_cli.__version__}"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{mse_cli.__version__}",
        help="version of %(prog)s binary",
    )

    subparsers = parser.add_subparsers(title="subcommands")

    context.add_subparser(subparsers)
    deploy.add_subparser(subparsers)
    init.add_subparser(subparsers)
    list_all.add_subparser(subparsers)
    login.add_subparser(subparsers)
    logout.add_subparser(subparsers)
    logs.add_subparser(subparsers)
    scaffold.add_subparser(subparsers)
    status.add_subparser(subparsers)
    stop.add_subparser(subparsers)
    test.add_subparser(subparsers)
    verify.add_subparser(subparsers)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")

    func(args)

    return 0


if __name__ == "__main__":
    main()
