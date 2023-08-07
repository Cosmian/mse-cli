"""mse_cli.home.command.code_provider.unseal module."""

import argparse
from pathlib import Path

from mse_lib_crypto.seal_box import unseal

from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("unseal", help="unseal file with X25519 private key")

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="path to the file to unseal",
    )

    parser.add_argument(
        "--private-key",
        required=True,
        type=Path,
        metavar="FILE",
        help="path to the raw X25519 private key",
    )

    parser.add_argument(
        "--output",
        type=Path,
        metavar="DIR",
        default=Path().cwd().resolve(),
        help="directory to write the unsealed file",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    if ".seal" not in args.input.suffixes:
        raise argparse.ArgumentTypeError("Input file must have .seal extension")

    output_path: Path = args.output / args.input.with_suffix("").name
    output_path.write_bytes(
        unseal(args.input.read_bytes(), args.private_key.read_bytes())
    )

    LOG.info("Decrypted file saved to: %s", output_path)
