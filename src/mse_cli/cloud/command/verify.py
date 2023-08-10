"""mse_cli.cloud.command.verify module."""

import argparse
import os
from pathlib import Path

from mse_cli.cloud.api.types import SSLCertificateOrigin
from mse_cli.cloud.command.helpers import prepare_code, verify_app
from mse_cli.cloud.model.context import Context
from mse_cli.error import RatlsVerificationNotSupported
from mse_cli.log import LOGGER as LOG


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
        help="domain name of the MSE web application (e.g. {uuid}.cosmian.io)",
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

    parser.add_argument(
        "--workspace",
        type=Path,
        required=False,
        help="directory to write the temporary files",
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
        context = Context.load(args.context, workspace=args.workspace)

        if context.instance.ssl_certificate_origin != SSLCertificateOrigin.Self:
            raise RatlsVerificationNotSupported(
                "The application is not using a certificate generated by MSE. "
                "Verifying the application is therefore not possible on use"
            )

        # Encrypt the code and create the tarball
        prepare_code(args.code, context)
        mrenclave = context

    verify_app(mrenclave, args.domain_name, Path(os.getcwd()) / "cert.pem")
