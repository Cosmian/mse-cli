"""Verify subparser definition."""

import os
from pathlib import Path
import tempfile

from intel_sgx_ra.error import SGXQuoteNotFound
from mse_lib_crypto.xsalsa20_poly1305 import decrypt_directory
from mse_ctl.cli.helpers import compute_mr_enclave, get_certificate, verify_app
from mse_ctl.conf.context import Context
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.fs import untar


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

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--skip-fingerprint',
                       action='store_true',
                       help='Do not verify the code fingerprint')

    group.add_argument('--fingerprint',
                       type=str,
                       help='Check the code fingerprint against that value')

    group.add_argument('--context',
                       type=Path,
                       metavar='path/to/context.tar',
                       help='Path to the context tarball')


def run(args):
    """Run the subcommand."""
    log.info("Checking your app...")

    # Compute MRENCLAVE and decrypt the code if needed
    mrenclave = None
    if args.fingerprint:
        mrenclave = args.fingerprint
    elif args.context:
        # Untar the context tarball
        workspace = Path(tempfile.mkdtemp())
        context_path = workspace / "context"
        os.makedirs(context_path)
        decrypted_code_path = workspace / "decrypted_code"
        untar(context_path, args.context)

        # Read the context file
        context = Context.from_toml(context_path /
                                    Context.get_context_filename())

        # Untar and decrypt the code tarball
        untar(decrypted_code_path,
              context_path / Context.get_tar_code_filename())
        decrypt_directory(decrypted_code_path, context.config.code_sealed_key)
        log.info("The code has been decrypted in: %s", decrypted_code_path)
        mrenclave = compute_mr_enclave(
            context, context_path / Context.get_tar_code_filename())

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
