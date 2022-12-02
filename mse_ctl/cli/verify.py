"""Verify subparser definition."""

import os
from pathlib import Path

from intel_sgx_ra.error import SGXQuoteNotFound
from mse_ctl.cli.helpers import (compute_mr_enclave, get_certificate,
                                 prepare_code, verify_app)
from mse_ctl.conf.context import Context
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "verify",
        help="Verify the trustworthiness of an MSE app (no sign-in required)")

    parser.set_defaults(func=run)

    parser.add_argument(
        'domain_name',
        type=str,
        help='The domain name of the MSE app (ex: demo.cosmian.app).')

    parser.add_argument('--skip-fingerprint',
                        action='store_true',
                        help='Do not verify the code fingerprint')

    parser.add_argument('--fingerprint',
                        type=str,
                        help='Check the code fingerprint against that value')

    parser.add_argument('--context',
                        type=Path,
                        metavar='path/to/context.mse',
                        help='Path to the context file')

    parser.add_argument('--code',
                        type=Path,
                        metavar='path/to/code',
                        help='Path to the plaintext code')


def run(args):
    """Run the subcommand."""
    log.info("Checking your app...")

    # Check args
    if args.skip_fingerprint and (args.fingerprint or args.context
                                  or args.code):
        print(
            "[--skip-fingerprint] and [--fingerprint] and [--context & --code] "
            "are mutually exclusive")
        return

    if args.fingerprint and (args.context or args.code):
        print(
            "[--skip-fingerprint] and [--fingerprint] and [--context & --code] "
            "are mutually exclusive")
        return

    if not args.fingerprint and not args.skip_fingerprint:
        if (args.context and not args.code) or (not args.context and args.code):
            print("[--context] and [--code] must be used together")
            return

    # Compute MRENCLAVE and decrypt the code if needed
    mrenclave = None
    if args.fingerprint:
        mrenclave = args.fingerprint
    elif args.context:
        # Read the context file
        context = Context.from_toml(args.context)

        # Encrypt the code and create the tarball
        (tar_path, _) = prepare_code(args.code, context)

        mrenclave = compute_mr_enclave(context, tar_path)

    # Get the certificate
    ca_data = get_certificate(args.domain_name)
    cert_path = Path(os.getcwd()) / "cert.pem"
    cert_path.write_text(ca_data)

    try:
        verify_app(mrenclave, ca_data)
    except SGXQuoteNotFound:
        log.info(
            "%sThe application is not using a certificate generate by mse.%s",
            bcolors.WARNING, bcolors.ENDC)
        log.info("Verifying the application is therefore not possible on use.")
        return

    log.info("Verification: %ssuccess%s", bcolors.OKGREEN, bcolors.ENDC)
    log.info("The verified certificate has been saved at: %s", cert_path)
