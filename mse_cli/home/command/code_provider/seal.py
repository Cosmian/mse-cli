"""mse_cli.home.command.code_provider.seal module."""

from pathlib import Path

from intel_sgx_ra.ratls import ratls_verify
from mse_lib_crypto.seal_box import seal

from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "seal", help="seal the secrets to be share with an MSE app"
    )

    parser.add_argument(
        "--secrets",
        type=Path,
        required=True,
        help="secret file to seal",
    )

    parser.add_argument(
        "--cert",
        required=True,
        type=Path,
        metavar="FILE",
        help="path to the ratls certificate",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="directory to write the sealed secrets file",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    quote = ratls_verify(args.cert)

    enclave_pk = quote.report_body.report_data[32:64]
    sealed_secrets = seal(args.secrets.read_bytes(), enclave_pk)

    sealed_secrets_path: Path = args.output / (args.secrets.name + ".sealed")
    sealed_secrets_path.write_bytes(sealed_secrets)

    LOG.info("Your sealed secrets has been saved at: %s", sealed_secrets_path)
