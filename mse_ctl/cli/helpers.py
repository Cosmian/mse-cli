"""Handlers functions."""

from datetime import datetime
import re
from pathlib import Path
import ssl
from typing import List, Optional
from uuid import UUID

import docker
import requests
from intel_sgx_ra.attest import remote_attestation
from intel_sgx_ra.ratls import ratls_verification
from intel_sgx_ra.signer import mr_signer_from_pk

from mse_ctl import MSE_CERTIFICATES_URL, MSE_DOCKER_IMAGE_URL, MSE_PCCS_URL
from mse_ctl.api.app import stop
from mse_ctl.api.auth import Connection
from mse_ctl.api.project import get_app_from_name, get_from_name
from mse_ctl.api.plan import get as get_plan
from mse_ctl.api.types import App, AppStatus, Plan, Project, SSLCertificateOrigin
from mse_ctl.conf.app import AppConf
from mse_ctl.conf.context import Context
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors


def get_enclave_size(conn: Connection, app: AppConf) -> int:
    """Get the enclave size from an app."""
    r: requests.Response = get_plan(conn=conn, name=app.plan)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    plan = Plan.from_json_dict(r.json())
    return plan.memory


def get_project_from_name(conn: Connection, name: str) -> Optional[Project]:
    """Get the project from its name."""
    r: requests.Response = get_from_name(conn=conn, project_name=name)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    project = r.json()
    if not project:
        return None

    return Project.from_json_dict(project[0])


def exists_in_project(conn: Connection, project_uuid: UUID, name: str,
                      status: Optional[List[AppStatus]]) -> Optional[App]:
    """Say whether the app exists in the project."""
    r: requests.Response = get_app_from_name(conn=conn,
                                             project_uuid=project_uuid,
                                             app_name=name,
                                             status=status)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    app = r.json()
    if not app:
        return None

    return App.from_json_dict(app[0])


def stop_app(conn: Connection, app_uuid: UUID):
    """Stop the app remotly."""
    r: requests.Response = stop(conn=conn, uuid=app_uuid)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")


def compute_mr_enclave(context: Context, tar_path: Path) -> str:
    """Compute the MR enclave of an enclave."""
    client = docker.from_env()
    image = f"{MSE_DOCKER_IMAGE_URL}:{context.docker_version}"

    # Pull always before running
    client.images.pull(image)

    command = [
        "--size", f"{context.enclave_size}G", "--code", "/tmp/service.tar",
        "--host", context.config_domain_name, "--application",
        context.python_application, "--dry-run"
    ]

    volumes = {f"{tar_path}": {'bind': '/tmp/service.tar', 'mode': 'rw'}}

    if context.ssl_certificate_origin == SSLCertificateOrigin.Owner:
        command.append("--certificate")
        command.append("/tmp/cert.pem")
        volumes[f"{context.app_cert_path}"] = {
            'bind': '/tmp/cert.pem',
            'mode': 'rw'
        }
    elif context.ssl_certificate_origin == SSLCertificateOrigin.Operator:
        command.append("--no-ssl")
    else:
        command.append("--self-signed")
        command.append(str(int(datetime.timestamp(context.expires_at))))

    if context.encrypted_code:
        command.append("--encrypted")

    container = client.containers.run(
        image,
        command=command,
        volumes=volumes,
        remove=True,
        detach=False,
        stdout=True,
        stderr=True,
    )

    # Save the docker output
    log.debug("Write docker logs in: %s", context.docker_log_path)
    context.docker_log_path.write_bytes(container)

    # Get the mr_enclave from the docker output
    pattern = 'mr_enclave:[ ]*([a-z0-9 ]{64})'
    m = re.search(pattern.encode("utf-8"), container)

    if not m:
        raise Exception(
            "Fail to compute mr_enclave!!! See {docker_log_path} for more details."
        )

    return str(m.group(1).decode("utf-8"))


def get_certificate(domain_name: str) -> str:
    """Get the certificate from `domain_name`."""
    return ssl.get_server_certificate((domain_name, 443))


def verify_app(mrenclave: Optional[str], ca_data: str):
    """Verify the app by proceeding the remote attestion."""
    # Compute MRSIGNER
    r = requests.get(url=MSE_CERTIFICATES_URL, timeout=60)
    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")
    mrsigner = mr_signer_from_pk(r.content)

    # Get the quote
    quote = ratls_verification(ca_data.encode('utf8'))

    # Proceed the RA.
    try:
        remote_attestation(quote=quote, base_url=MSE_PCCS_URL)
    except Exception as e:
        log.info("Verification: %sfailure%s", bcolors.FAIL, bcolors.ENDC)
        raise e

    if mrenclave:
        if quote.report_body.mr_enclave != bytes.fromhex(mrenclave):
            log.info("Verification: %sfailure%s", bcolors.FAIL, bcolors.ENDC)
            raise Exception(
                "MRENCLAVE is wrong "
                f"(read {bytes(quote.report_body.mr_enclave).hex()} "
                f"but should be {mrenclave})")
    else:
        log.info("%sMRENCLAVE check skipped!%s", bcolors.WARNING, bcolors.ENDC)

    if quote.report_body.mr_signer != mrsigner:
        log.info("Verification: %sfailure%s", bcolors.FAIL, bcolors.ENDC)
        raise Exception("MRSIGNER is wrong "
                        f"(read {bytes(quote.report_body.mr_signer).hex()} "
                        f"but should be {bytes(mrsigner).hex()})")
