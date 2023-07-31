"""mse_cli.home.command.code_provider.verify module."""

import shutil
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.serialization import Encoding

from mse_cli.core.enclave import compute_mr_enclave, verify_enclave
from mse_cli.home.command.helpers import get_client_docker, load_docker_image
from mse_cli.home.model.evidence import ApplicationEvidence
from mse_cli.home.model.package import CodePackage
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "verify",
        help="verify the trustworthiness of a running MSE web application "
        "and get the RA-TLS certificate",
    )

    parser.add_argument(
        "--evidence",
        required=True,
        type=Path,
        metavar="FILE",
        help="path to the evidence file",
    )

    parser.add_argument(
        "--package",
        type=Path,
        required=True,
        help="MSE package containing the Docker images and the code",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="output path of the verified RA-TLS certificate",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    if not args.output.is_dir():
        raise NotADirectoryError(f"{args.output} does not exist")

    workspace = Path(tempfile.mkdtemp(dir=args.output))
    log_path = workspace / "docker.log"

    evidence = ApplicationEvidence.load(args.evidence)

    LOG.info("Extracting the package at %s...", workspace)
    package = CodePackage.extract(workspace, args.package)

    LOG.info("A log file is generating at: %s", log_path)

    client = get_client_docker()
    image = load_docker_image(client, package.image_tar)
    mrenclave = compute_mr_enclave(
        client,
        image,
        evidence.input_args,
        workspace,
        log_path,
    )

    LOG.info("Fingerprint is: %s", mrenclave)

    try:
        verify_enclave(
            evidence.signer_pk,
            evidence.ratls_certificate,
            fingerprint=mrenclave,
            collaterals=evidence.collaterals,
        )
    except Exception as exc:
        LOG.error("Verification failed!")
        raise exc

    LOG.info("Verification successful")

    ratls_cert_path = args.output.resolve() / "ratls.pem"
    ratls_cert_path.write_bytes(
        evidence.ratls_certificate.public_bytes(encoding=Encoding.PEM)
    )

    LOG.info("The RA-TLS certificate has been saved at: %s", ratls_cert_path)

    # Clean up the workspace
    LOG.info("Cleaning up the temporary workspace...")
    shutil.rmtree(workspace)
