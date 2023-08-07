"""mse_cli.home.command.code_provider.seal module."""

from pathlib import Path

from intel_sgx_ra.quote import Quote
from intel_sgx_ra.ratls import ratls_verify
from mse_lib_crypto.seal_box import seal

from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "seal",
        help="seal file with recipient public key using either raw "
        "X25519 public key or RA-TLS certificate with enclave's "
        "public key in REPORT_DATA field of SGX quote",
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="path to the file to seal",
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--receiver-ratls-cert",
        type=Path,
        metavar="FILE",
        help="path to RA-TLS certificate",
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
        default=Path().cwd().resolve(),
        help="directory to write the sealed file",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    enclave_pk: bytes
    if args.receiver_ratls_cert:
        quote: Quote = ratls_verify(args.receiver_ratls_cert)
        enclave_pk = quote.report_body.report_data[32:64]
    else:
        enclave_pk = args.receiver_public_key.read_bytes()

    output_path: Path = args.output / f"{args.input.name}.seal"
    output_path.write_bytes(seal(args.input.read_bytes(), enclave_pk))

    LOG.info("Encrypted file saved to: %s", output_path)
