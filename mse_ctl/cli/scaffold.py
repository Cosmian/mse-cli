"""Scaffold subparser definition."""

from pathlib import Path
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "scaffold", help="Create a new empty project in the current directory")

    parser.set_defaults(func=run)

    parser.add_argument('--name',
                        required=True,
                        type=str,
                        help='The name of the empty project.')


def run(args):
    """Run the subcommand."""
    log.info("An empty project has been generated in the current directory.")
    log.info("You can configured your mse application in: name.yaml")
