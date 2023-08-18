"""mse_cli.home.command.code_provider.encrypt module."""

import sys
from pathlib import Path

from cryptography.fernet import Fernet

from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "encrypt", help="encrypt a file using Fernet symmetric encryption"
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="path to the file to encrypt",
    )

    parser.add_argument(
        "--key",
        type=Path,
        metavar="FILE",
        required=True,
        help="path to the file within a 32 bytes key URL Safe Base64 encoded",
    )

    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="path to write encrypted file",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    LOG.info("Encrypting %s...", args.input)

    key: bytes = args.key.read_bytes()
    data: bytes = args.input.read_bytes()

    encrypted_data: bytes = Fernet(key).encrypt(data)

    if args.output:
        args.output.write_bytes(encrypted_data)
        LOG.info("File encrypted to %s", args.output)
    else:
        LOG.info("Data sucessfully encrypted!")
        LOG.info(
            "----------------------------------------------------------------------"
        )
        sys.stdout.buffer.write(encrypted_data)
