"""Verify subparser definition."""

from pathlib import Path
import uuid
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "verify", help="Verify the trustworthiness of a MSE enclave")

    parser.set_defaults(func=run)

    parser.add_argument('--id',
                        required=True,
                        type=uuid.UUID,
                        help='The id of the MSE enclave.')


def run(args):
    """Run the subcommand."""
    log.info("Checking your enclave...")
