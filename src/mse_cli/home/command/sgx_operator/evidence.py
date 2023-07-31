"""mse_cli.home.command.sgx_operator.evidence module."""

import json
import socket
import ssl
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate
from docker.models.containers import Container
from intel_sgx_ra.attest import retrieve_collaterals
from intel_sgx_ra.ratls import get_server_certificate, ratls_verify

from mse_cli.core.no_sgx_docker import NoSgxDockerConfig
from mse_cli.core.sgx_docker import SgxDockerConfig
from mse_cli.home.command.helpers import get_client_docker, get_running_app_container
from mse_cli.home.model.evidence import ApplicationEvidence
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "evidence",
        help="collect the evidences to verify on offline mode "
        "the application and the enclave",
    )

    pccs_url_default = guess_pccs_url() or "https://pccs.example.com"
    parser.add_argument(
        "--pccs",
        type=str,
        help=f"URL to the PCCS (default: {pccs_url_default})",
        default=pccs_url_default,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="the directory to write the evidence file",
    )

    parser.add_argument(
        "name",
        type=str,
        help="the name of the application",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    if not args.output.is_dir():
        raise NotADirectoryError(f"`{args.output}` does not exist")

    client = get_client_docker()
    container = get_running_app_container(client, args.name)

    collect_evidence_and_certificate(
        container=container, pccs_url=args.pccs, output=args.output
    )


# pylint: disable=too-many-locals
def collect_evidence_and_certificate(
    container: Container,
    pccs_url: str,
    output: Path,
):
    """Collect evidence JSON file and RA-TLS certificate from running enclave."""
    LOG.info("Collecting the enclave and application evidences...")

    docker = SgxDockerConfig.load(container.attrs, container.labels)
    input_args = NoSgxDockerConfig.from_sgx(docker_config=docker)

    # Get the certificate from the application
    try:
        ratls_cert = load_pem_x509_certificate(
            get_server_certificate((docker.host, docker.port)).encode("utf-8")
        )
    except (ssl.SSLZeroReturnError, socket.gaierror, ssl.SSLEOFError) as exc:
        raise ConnectionError(
            f"Can't reach {docker.host}:{docker.port}. "
            "Are you sure the application is still running?"
        ) from exc

    quote = ratls_verify(ratls_cert)

    (
        tcb_info,
        qe_identity,
        tcb_cert,
        root_ca_crl,
        pck_platform_crl,
    ) = retrieve_collaterals(quote, pccs_url)

    signer_key = load_pem_private_key(
        docker.signer_key.read_bytes(),
        password=None,
    )

    evidence = ApplicationEvidence(
        input_args=input_args,
        ratls_certificate=ratls_cert,
        root_ca_crl=root_ca_crl,
        pck_platform_crl=pck_platform_crl,
        tcb_info=tcb_info,
        qe_identity=qe_identity,
        tcb_cert=tcb_cert,
        signer_pk=signer_key.public_key(),
    )

    evidence_path = output / "evidence.json"
    evidence.save(evidence_path)
    LOG.info("The evidence file has been generated at: %s", evidence_path)
    LOG.info("The evidence file can now be shared!")

    ratls_cert_path = output / "ratls.pem"
    ratls_cert_path.write_bytes(
        evidence.ratls_certificate.public_bytes(encoding=Encoding.PEM)
    )

    LOG.info("The RA-TLS certificate has been saved at: %s", ratls_cert_path)


def guess_pccs_url(
    aemsd_conf_file: Path = Path("/etc/sgx_default_qcnl.conf"),
) -> Optional[str]:
    """Get the pccs url from aesmd service configuration file."""
    try:
        with open(aemsd_conf_file, encoding="utf-8") as f:
            # The configuration is not a valid json: it contains comments
            # First remove them and then deserialize the json string
            content = f.readlines()
            content = [
                line
                for line in content
                if line.strip() and not line.strip().startswith("//")
            ]
            url = json.loads("".join(content)).get("pccs_url", None)

            if url:
                url = urlparse(url)
                return f"{url.scheme}://{url.netloc}"
    except Exception:  # pylint: disable=broad-except
        pass

    return None
