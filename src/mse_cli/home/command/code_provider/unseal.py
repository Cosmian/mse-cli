"""mse_cli.home.command.code_provider.unseal module."""

import sys
from pathlib import Path

from mse_lib_crypto.seal_box import unseal

from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("unseal", help="unseal file using NaCl's Seal Box")

    parser.add_argument(
        "--input",
        type=Path,
        metavar="FILE",
        required=True,
        help="path to the file to unseal",
    )

    parser.add_argument(
        "--private-key",
        type=Path,
        metavar="FILE",
        required=True,
        help="path to raw X25519 private key",
    )

    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="path to write the file unsealed",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    LOG.info("Unsealing %s...", args.input)

    private_key: bytes = args.private_key.read_bytes()
    encrypted_data: bytes = args.input.read_bytes()

    data: bytes = unseal(encrypted_data, private_key)

    if args.output:
        args.output.write_bytes(data)
        LOG.info("File successfully unsealed to %s", args.output)
    else:
        LOG.info("Data sucessfully unsealed!")
        LOG.info(
            "----------------------------------------------------------------------"
        )
        sys.stdout.buffer.write(data)
