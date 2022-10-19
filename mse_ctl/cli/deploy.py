"""Deploy subparser definition."""

import os
import re
import ssl
import time
from pathlib import Path
from typing import List, Optional, Set
from uuid import UUID

import docker
import requests
from cryptography import x509

from mse_ctl.api.auth import Connection
from mse_ctl.api.enclave import get, new
from mse_ctl.api.types import Enclave, EnclaveStatus
from mse_ctl.conf.enclave import CodeProtection, EnclaveConf
from mse_ctl.conf.service import Service
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.crypto import encrypt_directory
from mse_ctl.utils.fs import tar

# from mse_lib_sgx.conversion import ed25519_to_x25519_pk
# from mse_lib_sgx.crypto import seal


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("deploy",
                                   help="Deploy the application from the "
                                   "current directory into a MSE enclave")

    parser.set_defaults(func=run)


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    enclave_conf = EnclaveConf.from_toml()
    service_context = Service.from_enclave_conf(enclave_conf)

    log.info("Preparing your project...")
    tar_path = prepare_code(enclave_conf, service_context)

    log.info("Deploying your project...")
    conn = user_conf.get_connection()
    enclave = deploy_service(conn, enclave_conf, tar_path)

    log.info("Enclave creating for %s...", enclave_conf.service_name)
    enclave = wait_enclave_creation(conn, enclave.uuid)

    service_context.id = enclave.uuid
    service_context.domain_name = enclave.domain_name

    log.info("Enclave created with uuid: %s", enclave.uuid)

    log.info("Checking enclave thrustworthiness...")
    mr_enclave = compute_mr_enclave(enclave, service_context.workspace,
                                    tar_path)
    log.info("MR enclave is %s", mr_enclave)

    # ca_data = ssl.get_server_certificate(
    #     (enclave.domain_name, 443)).encode("utf-8")
    # cert_path = Path(
    #     f"{enclave_conf.service_name}_{enclave_conf.service_version}_cert.pem")
    # cert_path.write_bytes(ca_data)

    # TODO: RA

    log.info("Unsealing your code and your private data from the enclave.")

    # cert = x509.load_pem_x509_certificate(ca_data)
    # x25519_pk: bytes = ed25519_to_x25519_pk(cert.public_key())

    # requests.post(url=enclave.domain_name,
    #               data=seal(data=b"hello", recipient_public_key=x25519_pk),
    #               headers={'Content-Type': 'application/octet-stream'},
    #               verify=str(cert_path.resolve()))

    log.info("Your application is now fully deployed and started.")

    # TODO

    log.info("It's now ready to be used on https://%s", enclave.domain_name)

    service_context.save()

    log.info("The context of this creation has been saved at: %s",
             service_context.path)


def prepare_code(enclave_conf: EnclaveConf,
                 service_context: Service,
                 patterns: Optional[List[str]] = None,
                 file_exceptions: Optional[List[str]] = None,
                 dir_exceptions: Optional[List[str]] = None) -> Path:
    """Tar and encrypt if required the Service Python code."""
    # TODO: check that with much more complicated python_flask_module (with dots)
    if not (Path(enclave_conf.code_location) /
            (enclave_conf.python_flask_module + ".py")).exists():
        raise FileNotFoundError(
            f"Flask module '{enclave_conf.python_flask_module}' "
            f"not found in {enclave_conf.code_location}!")

    src_path = Path(enclave_conf.code_location).resolve()

    if enclave_conf.code_protection == CodeProtection.Encrypted:

        log.debug("Encrypt code in %s to %s...", enclave_conf.code_location,
                  service_context.encrypted_code_path)

        whitelist: Set[str] = {"requirements.txt"}

        encrypt_directory(
            dir_path=Path(enclave_conf.code_location),
            patterns=(["*"] if patterns is None else patterns),
            key=service_context.symkey,
            exceptions=(list(whitelist) if file_exceptions is None else
                        list(set(file_exceptions) | whitelist)),
            dir_exceptions=([] if dir_exceptions is None else dir_exceptions),
            out_dir_path=service_context.encrypted_code_path)

        src_path = service_context.encrypted_code_path

    tar_path = tar(dir_path=src_path, tar_path=service_context.tar_code_path)

    log.debug("Tar encrypted code in '%s'", tar_path.name)

    return tar_path


def deploy_service(conn: Connection, enclave_conf: EnclaveConf,
                   tar_path: Path) -> Enclave:
    """Deploy the service to an enclave."""
    r: requests.Response = new(conn=conn,
                               conf=enclave_conf,
                               code_tar_path=tar_path)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    return Enclave.from_json_dict(r.json())


def wait_enclave_creation(conn: Connection, uuid: UUID) -> Enclave:
    """Wait for the enclave to be fully deployed."""
    while True:
        time.sleep(1)

        r: requests.Response = get(conn=conn, uuid=uuid)
        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        enclave = Enclave.from_json_dict(r.json())

        if enclave.status == EnclaveStatus.Running:
            break
        if enclave.status == EnclaveStatus.OnError:
            raise Exception(
                "The enclave creation stopped because an error occured...")
        if enclave.status == EnclaveStatus.Deleted:
            raise Exception("The enclave creation stopped because it "
                            " has been deleted in the meantimes...")

    return enclave


def compute_mr_enclave(enclave: Enclave, workspace: Path,
                       tar_path: Path) -> str:
    """Compute the MR enclave of an enclave."""
    client = docker.from_env()
    container = client.containers.run(
        os.getenv('MSE_CTL_DOCKER_REMOTE_URL', "mse-enclave:latest"),
        command=[
            enclave.enclave_size.value,
            str(enclave.enclave_lifetime), enclave.domain_name,
            str(enclave.port), enclave.code_protection.value, "--dry-run"
        ],
        volumes={f"{tar_path}": {
            'bind': '/tmp/service.tar',
            'mode': 'rw'
        }},
        remove=True,
        detach=False,
        stdout=True,
        stderr=True,
    )

    # Save the docker output
    docker_log_path = workspace / 'docker.log'
    log.debug("Write docker logs in: %s", docker_log_path)
    docker_log_path.write_bytes(container)

    # Get the mr_enclave from the docker output
    pattern = 'mr_enclave:[ ]*([a-z0-9 ]{64})'
    m = re.search(pattern.encode("utf-8"), container)

    if not m:
        raise Exception(
            "Fail to compute mr_enclave!!! See {docker_log_path} for more details."
        )

    return str(m.group(1))
