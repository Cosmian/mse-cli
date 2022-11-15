"""Verify subparser definition."""

import os

from pathlib import Path

from mse_ctl.cli.helpers import compute_mr_enclave, get_certificate, verify_app
from mse_ctl.conf.context import Context
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.crypto import decrypt_directory
from mse_ctl.utils.fs import untar


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "verify",
        help="Verify the trustworthiness of an MSE app (no sign-in required)")

    parser.set_defaults(func=run)

    parser.add_argument(
        '--domain-name',
        type=str,
        help='The domain name of the MSE app (ex: demo.cosmian.app).',
        required=True)

    parser.add_argument('--skip-mrenclave',
                        action='store_true',
                        help='Do not verify mrenclave.')

    parser.add_argument('--mrenclave',
                        type=str,
                        help='Check the mrenclave against that value.')

    parser.add_argument('--context',
                        type=Path,
                        metavar='path/to/context/uuid.mse',
                        help='Path to the context file to use '
                        'to recompute the mrenclave and verify it.')

    parser.add_argument('--code',
                        type=Path,
                        metavar='path/to/code.tar',
                        help='Path to the code tarball.')


def run(args):
    """Run the subcommand."""
    log.info("Checking your app...")

    # Check args
    if args.skip_mrenclave and (args.mrenclave or args.context or args.code):
        print("[--skip-mrenclave] and [--mrenclave] and [--context | --code] "
              "are mutually exclusive")
        return

    if args.mrenclave and (args.context or args.code):
        print("[--skip-mrenclave] and [--mrenclave] and [--context | --code] "
              "are mutually exclusive")
        return

    if not args.mrenclave and not args.skip_mrenclave:
        if (args.context and not args.code) or (not args.context and args.code):
            print("[--context] and [--code] must be used together")
            return

    # Compute MRENCLAVE and decrypt the code if needed
    mrenclave = None
    if args.mrenclave:
        mrenclave = args.mrenclave
    elif args.context:
        context = Context.from_toml(args.context)
        if context.encrypted_code:
            untar(context.decrypted_code_path, context.tar_code_path)
            decrypt_directory(context.decrypted_code_path, context.symkey)
            log.info("The code has been decrypted in: %s",
                     context.decrypted_code_path)
        mrenclave = compute_mr_enclave(context, args.code)

    # Get the certificate
    ca_data = get_certificate(args.domain_name)
    cert_path = Path(os.getcwd()) / "cert.pem"
    cert_path.write_text(ca_data)

    verify_app(mrenclave, ca_data)

    log.info("Verification: %ssuccess%s", bcolors.OKGREEN, bcolors.ENDC)
    log.info("The verified certificate has been saved at: %s", cert_path)
