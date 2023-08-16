"""mse_cli.cloud.command.helpers module."""

import socket
import ssl
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, no_type_check
from uuid import UUID

import docker
import requests
from intel_sgx_ra.error import SGXQuoteNotFound
from intel_sgx_ra.ratls import get_server_certificate
from mse_lib_crypto.xsalsa20_poly1305 import encrypt_directory

from mse_cli import MSE_CERTIFICATES_URL, MSE_PCCS_URL
from mse_cli.cloud.api.app import default, get, metrics, stop
from mse_cli.cloud.api.auth import Connection
from mse_cli.cloud.api.hardware import get as get_hardware
from mse_cli.cloud.api.project import get_app_from_name, get_from_name
from mse_cli.cloud.api.types import (
    App,
    AppStatus,
    DefaultAppConfig,
    Hardware,
    PartialApp,
    Project,
    SSLCertificateOrigin,
)
from mse_cli.cloud.model.context import Context
from mse_cli.core.clock_tick import ClockTick
from mse_cli.core.enclave import compute_mr_enclave, verify_enclave
from mse_cli.core.fs import tar
from mse_cli.core.ignore_file import IgnoreFile
from mse_cli.core.no_sgx_docker import NoSgxDockerConfig
from mse_cli.core.spinner import Spinner
from mse_cli.error import (
    RatlsVerificationFailure,
    RatlsVerificationNotSupported,
    UnexpectedResponse,
)
from mse_cli.log import LOGGER as LOG


def get_client_docker() -> docker.client.DockerClient:
    """Create a Docker client or exit if daemon is down."""
    try:
        return docker.from_env()
    except docker.errors.DockerException:
        LOG.warning("Docker seems not running. Please enable Docker daemon.")
        LOG.info("MSE needs Docker to verify the app trustworthiness.")
        LOG.info("Please refer to the documentation for more details.")
        sys.exit(1)


def get_default(conn: Connection) -> DefaultAppConfig:
    """Get a default app configuration from the backend."""
    r: requests.Response = default(conn=conn)
    if not r.ok:
        raise UnexpectedResponse(r.text)

    return DefaultAppConfig.from_dict(r.json())


def get_app(conn: Connection, app_id: UUID) -> App:
    """Get an app from the backend."""
    r: requests.Response = get(conn=conn, app_id=app_id)
    if not r.ok:
        raise UnexpectedResponse(r.text)

    return App.from_dict(r.json())


def get_metrics(conn: Connection, app_id: UUID) -> Dict[str, Any]:
    """Get the app metrics from the backend."""
    r: requests.Response = metrics(conn=conn, app_id=app_id)
    if not r.ok:
        raise UnexpectedResponse(r.text)

    return r.json()


def get_enclave_resources(conn: Connection, resource_name: str) -> Tuple[int, float]:
    """Get the enclave size and cores from an app."""
    r: requests.Response = get_hardware(conn=conn, name=resource_name)

    if not r.ok:
        raise UnexpectedResponse(r.text)

    hardware = Hardware.from_dict(r.json())
    return hardware.enclave_size, hardware.cores


def get_project_from_name(conn: Connection, name: str) -> Optional[Project]:
    """Get the project from its name."""
    r: requests.Response = get_from_name(conn=conn, project_name=name)

    if not r.ok:
        raise UnexpectedResponse(r.text)

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
    conn: Connection, project_id: UUID, name: str, status: Optional[List[AppStatus]]
) -> Optional[PartialApp]:
    """Say whether the app exists in the project."""
    r: requests.Response = get_app_from_name(
        conn=conn, project_id=project_id, app_name=name, status=status
    )

    if not r.ok:
        raise UnexpectedResponse(r.text)

    app = r.json()
    if not app:
        return None

    return PartialApp.from_dict(app[0])


def stop_app(conn: Connection, app_id: UUID) -> None:
    """Stop the app remotely."""
    r: requests.Response = stop(conn=conn, app_id=app_id)

    if not r.ok:
        raise UnexpectedResponse(r.text)

    clock = ClockTick(period=3, timeout=60, message="Timeout occured! Try again later.")
    while clock.tick():
        app = get_app(conn=conn, app_id=app_id)
        if app.is_terminated():
            break

    # Remove context file
    Context.clean(app_id, ignore_errors=True)


def non_empty_string(s):
    """Check if a string is empty for argparse cmdline."""
    if not s:
        raise ValueError("String cannot be empty")
    return s


@no_type_check
def verify_app(
    mrenclave: Optional[Union[str, Context]],
    domain_name: str,
    output_cert_path: Optional[Path],
):
    """Verify the app by proceeding the remote attestation."""
    if not mrenclave:
        LOG.warning("Code fingerprint check skipped!")
    elif not isinstance(mrenclave, str):
        # Compute the MREnclave
        context = mrenclave
        with Spinner("Computing the code fingerprint... "):
            mrenclave = compute_mr_enclave(
                get_client_docker(),
                context.config.docker,
                NoSgxDockerConfig(
                    subject=(
                        f"CN={context.instance.config_domain_name},"
                        "O=Cosmian Tech,"
                        "C=FR,"
                        "L=Paris,"
                        "ST=Ile-de-France"
                    ),
                    subject_alternative_name=context.instance.config_domain_name,
                    expiration_date=int(datetime.timestamp(context.instance.expires_at))
                    if context.instance.ssl_certificate_origin
                    != SSLCertificateOrigin.Owner
                    else None,
                    size=context.instance.enclave_size,
                    app_id=context.instance.id,
                    application=context.config.python_application,
                ),
                context.workspace,
                context.docker_log_path,
            )
        LOG.info("The code fingerprint is %s", mrenclave)

    # Get the ratls certificate
    try:
        ratls_cert = get_server_certificate((domain_name, 443))
        output_cert_path.write_text(ratls_cert)
    except (ssl.SSLZeroReturnError, socket.gaierror, ssl.SSLEOFError) as exc:
        raise ConnectionError(
            f"Can't reach {domain_name}. "
            "Are you sure the application is still running?"
        ) from exc

    # Get the signer key public key
    r = requests.get(url=MSE_CERTIFICATES_URL, timeout=60)
    if not r.ok:
        raise UnexpectedResponse(
            f"Can't get the enclave signer public key: [{r.status_code}] {r.text}",
        )

    try:
        verify_enclave(
            r.content, ratls_cert.encode("utf8"), mrenclave, pccs_url=MSE_PCCS_URL
        )
    except SGXQuoteNotFound as exc:
        raise RatlsVerificationNotSupported(
            "The application is not using a certificate generated by MSE. "
            "Verifying the application is therefore not possible on use"
        ) from exc
    except RatlsVerificationFailure as exc:
        LOG.error("Verification failed!")
        raise exc

    LOG.success("Verification success")  # type: ignore
    if output_cert_path:
        LOG.info("The verified certificate has been saved at: %s", output_cert_path)
