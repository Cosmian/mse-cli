"""Verify subparser definition."""

import uuid

from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "verify", help="Verify the trustworthiness of an MSE app")

    parser.set_defaults(func=run)

    parser.add_argument('--id',
                        required=True,
                        type=uuid.UUID,
                        help='The id of the MSE app.')


def run(args):
    """Run the subcommand."""
    log.info("Checking your app...")
