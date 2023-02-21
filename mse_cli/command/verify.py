"""mse_cli.command.verify module."""

import argparse
import os
import socket
import ssl
from pathlib import Path

from intel_sgx_ra.error import SGXQuoteNotFound

from mse_cli.command.helpers import (
    compute_mr_enclave,
    get_certificate,
    prepare_code,
    verify_app,
)
from mse_cli.conf.context import Context
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.spinner import Spinner


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "verify",
        help="verify the trustworthiness of a running MSE web application "
        "(no sign-in required)",
    )

    parser.set_defaults(func=run)

    parser.add_argument(
        "domain_name",
        type=str,
        help="domain name of the MSE web application (e.g. {uuid}.cosmian.app)",
    )

    parser.add_argument(
        "--fingerprint",
        type=str,
        metavar="HEXDIGEST",
        help="check the code fingerprint against specific SHA-256 hexdigest",
    )

    parser.add_argument(
        "--context",
        type=Path,
        metavar="FILE",
        help="path to the context file (should be used with --code)",
    )

    parser.add_argument(
        "--code",
        type=Path,
        metavar="DIR",
        help="path to the folder with unencrypted Python code "
        "(should be used with --context)",
    )


def run(args) -> None:
    """Run the subcommand."""
    LOG.info("Checking your app...")

    # Check args
    if args.fingerprint and (args.context or args.code):
        raise argparse.ArgumentTypeError(
            "[--fingerprint] and [--context & --code] are mutually exclusive"
        )

    if (args.context and not args.code) or (not args.context and args.code):
        raise argparse.ArgumentTypeError(
            "[--context] and [--code] must be used together"
        )

    # Compute MRENCLAVE and decrypt the code if needed
    mrenclave = None
    if args.fingerprint:
        mrenclave = args.fingerprint
    elif args.context:
        # Read the context file
        context = Context.from_toml(args.context)

        # Encrypt the code and create the tarball
        (tar_path, _) = prepare_code(args.code, context)

        with Spinner("Computing the code fingerprint... "):
            mrenclave = compute_mr_enclave(context, tar_path)

    # Get the certificate
    try:
        ca_data = get_certificate(args.domain_name)
        cert_path = Path(os.getcwd()) / "cert.pem"
        cert_path.write_text(ca_data)
    except (ssl.SSLZeroReturnError, socket.gaierror, ssl.SSLEOFError) as exc:
        raise ConnectionError(
            f"Can't reach {args.domain_name}. Are you sure the application is still running?"
        ) from exc

    try:
        verify_app(mrenclave, ca_data)
    except SGXQuoteNotFound:
        LOG.warning("The application is not using a certificate generated by MSE")
        LOG.info("Verifying the application is therefore not possible on use")
        return

    LOG.success("Verification success")  # type: ignore
    LOG.info("The verified certificate has been saved at: %s", cert_path)
