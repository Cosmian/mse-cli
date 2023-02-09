"""mse_cli.command.helpers module."""

import re
import socket
import ssl
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import docker
import requests
from intel_sgx_ra.attest import remote_attestation
from intel_sgx_ra.ratls import ratls_verification
from intel_sgx_ra.signer import mr_signer_from_pk
from mse_lib_crypto.xsalsa20_poly1305 import encrypt_directory

from mse_cli import MSE_CERTIFICATES_URL, MSE_PCCS_URL
from mse_cli.api.app import get, stop
from mse_cli.api.auth import Connection
from mse_cli.api.plan import get as get_plan
from mse_cli.api.project import get_app_from_name, get_from_name
from mse_cli.api.types import (
    App,
    AppStatus,
    PartialApp,
    Plan,
    Project,
    SSLCertificateOrigin,
)
from mse_cli.conf.context import Context
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.clock_tick import ClockTick
from mse_cli.utils.fs import tar
from mse_cli.utils.ignore_file import IgnoreFile


def get_client_docker() -> docker.client.DockerClient:
    """Create a Docker client or exit if daemon is down."""
    try:
        return docker.from_env()
    except docker.errors.DockerException:
        LOG.warning("Docker seems not running. Please enable Docker daemon.")
        LOG.info("MSE needs Docker to verify the app trustworthiness.")
        LOG.info("Please refer to the documentation for more details.")
        sys.exit(1)


def get_app(conn: Connection, uuid: UUID) -> App:
    """Get an app from the backend."""
    r: requests.Response = get(conn=conn, uuid=uuid)
    if not r.ok:
        raise Exception(r.text)

    return App.from_dict(r.json())


def get_enclave_resources(conn: Connection, resource_name: str) -> Tuple[int, float]:
    """Get the enclave size and cores from an app."""
    r: requests.Response = get_plan(conn=conn, name=resource_name)

    if not r.ok:
        raise Exception(r.text)

    plan = Plan.from_dict(r.json())
    return plan.memory, plan.cores


def get_project_from_name(conn: Connection, name: str) -> Optional[Project]:
    """Get the project from its name."""
    r: requests.Response = get_from_name(conn=conn, project_name=name)

    if not r.ok:
        raise Exception(r.text)

    project = r.json()
    if not project:
        return None

    return Project.from_dict(project[0])


def prepare_code(
    src_path: Path,
    context: Context,
) -> Tuple[Path, Dict[str, bytes]]:
    """Tar and encrypt (if required) the app python code."""
    LOG.debug("Encrypt code in %s to %s...", src_path, context.encrypted_code_path)

    nonces = encrypt_directory(
        dir_path=src_path,
        pattern="*",
        key=context.config.code_secret_key,
        nonces=context.instance.nonces if context.instance else None,
        exceptions=["requirements.txt"],
        ignore_patterns=list(IgnoreFile.parse(src_path)),
        out_dir_path=context.encrypted_code_path,
    )

    tar_path = tar(dir_path=context.encrypted_code_path, tar_path=context.tar_code_path)

    LOG.debug("Tar encrypted code in '%s'", tar_path.name)
    return tar_path, nonces


def exists_in_project(
    conn: Connection, project_uuid: UUID, name: str, status: Optional[List[AppStatus]]
) -> Optional[PartialApp]:
    """Say whether the app exists in the project."""
    r: requests.Response = get_app_from_name(
        conn=conn, project_uuid=project_uuid, app_name=name, status=status
    )

    if not r.ok:
        raise Exception(r.text)

    app = r.json()
    if not app:
        return None

    return PartialApp.from_dict(app[0])


def stop_app(conn: Connection, app_uuid: UUID) -> None:
    """Stop the app remotely."""
    r: requests.Response = stop(conn=conn, uuid=app_uuid)

    if not r.ok:
        raise Exception(r.text)

    clock = ClockTick(period=3, timeout=60, message="Timeout occured! Try again later.")
    while clock.tick():
        app = get_app(conn=conn, uuid=app_uuid)
        if app.is_terminated():
            break

    # Remove context file
    Context.clean(app_uuid, ignore_errors=True)


def compute_mr_enclave(context: Context, tar_path: Path) -> str:
    """Compute the MR enclave of an enclave."""
    client = get_client_docker()

    assert context.instance

    # Pull always before running
    client.images.pull(context.config.docker)

    command = [
        "--size",
        f"{context.instance.enclave_size}M",
        "--code",
        "/tmp/app.tar",
        "--host",
        context.instance.config_domain_name,
        "--uuid",
        str(context.instance.id),
        "--application",
        context.config.python_application,
        "--dry-run",
    ]

    volumes = {f"{tar_path}": {"bind": "/tmp/app.tar", "mode": "rw"}}

    if context.instance.ssl_certificate_origin == SSLCertificateOrigin.Owner:
        command.append("--certificate")
        command.append("/tmp/cert.pem")
        volumes[f"{context.app_cert_path}"] = {"bind": "/tmp/cert.pem", "mode": "rw"}
    else:
        command.append("--self-signed")
        command.append(str(int(datetime.timestamp(context.instance.expires_at))))

    container = client.containers.run(
        context.config.docker,
        command=command,
        volumes=volumes,
        entrypoint="mse-run",
        remove=True,
        detach=False,
        stdout=True,
        stderr=True,
    )

    # Save the docker output
    LOG.debug("Write docker logs in: %s", context.docker_log_path)
    context.docker_log_path.write_bytes(container)

    # Get the mr_enclave from the docker output
    pattern = "mr_enclave:[ ]*([a-z0-9 ]{64})"
    m = re.search(pattern.encode("utf-8"), container)

    if not m:
        raise Exception(
            "Fail to compute mr_enclave! See {docker_log_path} for more details."
        )

    return str(m.group(1).decode("utf-8"))


def get_certificate(domain_name: str) -> str:
    """Get TLS certificate from `domain_name`.

    Notes
    -----
    Don't use `ssl.get_server_certificate()` because there are some
    issues with Server Name Indication (SNI) extension on some
    OpenSSL/LibreSSL versions (particularly MacOS).

    """
    with socket.create_connection((domain_name, 443)) as sock:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with context.wrap_socket(sock, server_hostname=domain_name) as ssock:
            cert = ssock.getpeercert(True)
            if not cert:
                raise Exception("Can't get peer certificate")
            return ssl.DER_cert_to_PEM_cert(cert)


def verify_app(mrenclave: Optional[str], ca_data: str):
    """Verify the app by proceeding the remote attestation."""
    r = requests.get(url=MSE_CERTIFICATES_URL, timeout=60)
    if not r.ok:
        raise Exception(r.text)
    # Compute MRSIGNER value from public key
    mrsigner = mr_signer_from_pk(r.content)

    # Check certificate's public key in quote's user report data
    quote = ratls_verification(ca_data.encode("utf8"))

    # Proceed RA
    try:
        remote_attestation(quote=quote, base_url=MSE_PCCS_URL)
    except Exception as exc:
        LOG.error("Verification failed!")
        raise exc

    if mrenclave:
        if quote.report_body.mr_enclave != bytes.fromhex(mrenclave):
            LOG.error("Verification failed!")
            raise Exception(
                "Code fingerprint is wrong "
                f"(read {bytes(quote.report_body.mr_enclave).hex()} "
                f"but should be {mrenclave})"
            )
    else:
        LOG.warning("Code fingerprint check skipped!")

    if quote.report_body.mr_signer != mrsigner:
        LOG.error("Verification failed!")
        raise Exception(
            "Enclave signer is wrong "
            f"(read {bytes(quote.report_body.mr_signer).hex()} "
            f"but should be {bytes(mrsigner).hex()})"
        )


def non_empty_string(s):
    """Check if a string is empty for argparse cmdline."""
    if not s:
        raise ValueError("String cannot be empty")
    return s
