"""mse_cli.main module."""

import argparse
from enum import Enum
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
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.color import COLOR, setup_color
from mse_cli.log import setup_logging


class ColorMode(str, Enum):
    never = "never"
    always = "always"


def main() -> int:
    """Entrypoint of the CLI."""
    parser = argparse.ArgumentParser(
        description="MicroService Encryption CLI" f" - {mse_cli.__version__}"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{mse_cli.__version__}",
        help="version of %(prog)s binary",
    )

    parser.add_argument(
        "--color",
        type=ColorMode,
        default=1,
        help="able (default) or disable the stdout/stderr colors",
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

    setup_color(args.color == ColorMode.always)
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
        LOG.error(e)
        return 1


if __name__ == "__main__":
    main()
