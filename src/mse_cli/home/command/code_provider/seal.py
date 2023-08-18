"""mse_cli.home.command.code_provider.seal module."""

import sys
from pathlib import Path

from intel_sgx_ra.quote import Quote
from intel_sgx_ra.ratls import ratls_verify
from mse_lib_crypto.seal_box import seal

from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "seal",
        help="seal file using NaCl's Seal Box."
        "Recipient is either raw X25519 public key or "
        "extracted from RA-TLS certificate with enclave's "
        "public key in REPORT_DATA field of SGX quote",
    )

    parser.add_argument(
        "--input",
        type=Path,
        metavar="FILE",
        required=True,
        help="path to the file to seal",
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--receiver-enclave",
        type=Path,
        metavar="FILE",
        help="path to RA-TLS certificate of the enclave",
    )

    group.add_argument(
        "--receiver-public-key",
        type=Path,
        metavar="FILE",
        help="path to raw X25519 public key",
    )

    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="path to write the file sealed",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    LOG.info("Sealing %s...", args.input)

    enclave_pk: bytes
    if args.receiver_enclave:
        quote: Quote = ratls_verify(args.receiver_enclave)
        enclave_pk = quote.report_body.report_data[32:64]
    else:
        enclave_pk = args.receiver_public_key.read_bytes()

    encrypted_data: bytes = seal(args.input.read_bytes(), enclave_pk)

    if args.output:
        args.output.write_bytes(encrypted_data)
        LOG.info("File sealed to %s", args.output)
    else:
        LOG.info("Data sucessfully sealed!")
        LOG.info(
            "----------------------------------------------------------------------"
        )
        sys.stdout.buffer.write(encrypted_data)
