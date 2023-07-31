"""mse_cli.home.command.code_provider.decrypt module."""

import sys
from pathlib import Path

from cryptography.fernet import Fernet

from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "decrypt", help="decrypt a file using Fernet symmetric encryption"
    )

    parser.add_argument(
        "--key",
        type=Path,
        required=True,
        help="path to the file within a 32 bytes key URL Safe Base64 encoded",
    )

    parser.add_argument(
        "file",
        type=Path,
        help="file to decrypt",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="file to write decrypted result",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    LOG.info("Decrypting %s...", args.file)

    key: bytes = args.key.read_bytes()
    encrypted_data: bytes = args.file.read_bytes()

    data: bytes = Fernet(key).decrypt(encrypted_data)

    if args.output:
        args.output.write_bytes(data)
        LOG.info("File sucessfully decrypted to %s", args.output)
    else:
        try:
            LOG.info("Data sucessfully decrypted!")
            LOG.info(
                "----------------------------------------------------------------------"
            )
            sys.stdout.write(data.decode("utf-8"))
        except UnicodeDecodeError:
            sys.stdout.write(data.hex())
