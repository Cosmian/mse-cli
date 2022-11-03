"""Deploy subparser definition."""

import time
from pathlib import Path
from typing import List, Optional, Set
from uuid import UUID

import requests
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from requests import ReadTimeout

from mse_ctl.api.app import get, new
from mse_ctl.api.auth import Connection
from mse_ctl.api.types import App, AppStatus
from mse_ctl.cli.helpers import (compute_mr_enclave, exists_in_project,
                                 get_certificate_and_save,
                                 get_project_from_name, stop_app, verify_app)
from mse_ctl.conf.app import AppConf, CodeProtection
from mse_ctl.conf.context import Context
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.crypto import ed25519_to_x25519_pubkey, encrypt_directory, seal
from mse_ctl.utils.fs import tar


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("deploy",
                                   help="Deploy the application from the "
                                   "current directory into a MSE node")

    parser.set_defaults(func=run)


# pylint: disable=unused-argument
def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    app_conf = AppConf.from_toml()
    conn = user_conf.get_connection()

    if not check_app_conf(conn, app_conf):
        return

    log.info("Preparing your app...")
    context = Context.from_app_conf(app_conf)
    tar_path = prepare_code(Path(app_conf.code_location).resolve(), context)

    log.info("Deploying your app...")
    app = deploy_app(conn, app_conf, tar_path)

    log.info("App creating for %s:%s...", app.name, app.version)
    app = wait_app_creation(conn, app.uuid)

    context.run(app.uuid, app.domain_name,
                "develop")  # TODO: unhardcode develop
    log.info("App created with uuid: %s", app.uuid)

    log.info("Checking app thrustworthiness...")
    cert = get_certificate_and_save(app.domain_name, context.cert_path)
    mr_enclave = compute_mr_enclave(context, tar_path)
    log.info("MR enclave is %s", mr_enclave)
    verify_app(mr_enclave, cert)
    log.info("Verification: %ssuccess%s", bcolors.OKGREEN, bcolors.ENDC)
    log.info("The verified certificate has been saved at: %s",
             context.cert_path)

    if app.code_protection == CodeProtection.Encrypted:
        log.info(
            "Unsealing your code and your private data from the enclave...")
        send_seal_key(context, cert)

    log.info("Waiting for application to be ready...")
    check_app_health(context, app.health_check_endpoint)

    log.info("Your application is now fully deployed and started...")
    log.info("It's now ready to be used on https://%s", app.domain_name)

    context.save()

    log.info("The context of this creation has been saved at: %s",
             context.exported_path)


def check_app_health(context: Context, health_check_endpoint: str):
    """Return True when the app is ready and up."""
    while True:
        try:
            r = requests.get(
                url=f"https://{context.domain_name}{health_check_endpoint}",
                verify=str(context.cert_path.resolve()),
                timeout=2)

            if r.ok and r.status_code == 200 \
               and r.content != b"Waiting for sealed symmetric key...":
                # TODO: use header banner in the response?
                break
        except ReadTimeout:
            # Ignore the error, server is not ready yet
            pass
        except requests.exceptions.SSLError:
            # Ignore the error, server is not ready yet
            pass

        time.sleep(2)

    return True


def check_app_conf(conn: Connection, app_conf: AppConf) -> bool:
    """Check app conf: project exist, app name exist, etc."""
    # Check that project exists
    project = get_project_from_name(conn, app_conf.project)
    if not project:
        raise Exception(f"Project {app_conf.project} does not exist")

    # Check that a same name application is not running yet
    app = exists_in_project(conn, project.uuid, app_conf.name, [
        AppStatus.Initializing,
        AppStatus.Running,
        AppStatus.OnError,
    ])

    if app:
        log.info(
            "An application with the same name in that project is already running..."
        )
        answer = input("Would you like to replace it [yes/no]? ")
        if answer.lower() in ["y", "yes"]:
            log.info("Stopping the previous app...")
            stop_app(conn, app.uuid)
        else:
            log.info("Your deployment has been stopped!")
            return False

    # TODO: check that with much more complicated python_flask_module (with dots)
    if not (Path(app_conf.code_location) /
            (app_conf.python_module + ".py")).exists():
        raise FileNotFoundError(f"Flask module '{app_conf.python_module}' "
                                f"not found in {app_conf.code_location}!")

    return True


def deploy_app(conn: Connection, app_conf: AppConf, tar_path: Path) -> App:
    """Deploy the app to a mse node."""
    r: requests.Response = new(conn=conn, conf=app_conf, code_tar_path=tar_path)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    return App.from_json_dict(r.json())


def wait_app_creation(conn: Connection, uuid: UUID) -> App:
    """Wait for the app to be fully deployed."""
    while True:
        time.sleep(1)

        r: requests.Response = get(conn=conn, uuid=uuid)
        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        app = App.from_json_dict(r.json())

        if app.status == AppStatus.Running:
            break
        if app.status == AppStatus.OnError:
            raise Exception(
                "The app creation stopped because an error occured...")
        if app.status == AppStatus.Deleted:
            raise Exception("The app creation stopped because it "
                            " has been deleted in the meantimes...")
        if app.status == AppStatus.Stopped:
            raise Exception("The app creation stopped because it "
                            " has been stopped in the meantimes...")

    return app


def send_seal_key(context: Context, ca_data: bytes):
    """Send the key which was used to encrypt the code."""
    cert = x509.load_pem_x509_certificate(ca_data)
    x25519_pk: bytes = ed25519_to_x25519_pubkey(cert.public_key().public_bytes(
        encoding=Encoding.Raw, format=PublicFormat.Raw))

    r = requests.post(url=f"https://{context.domain_name}",
                      data=seal(data=context.symkey,
                                recipient_public_key=x25519_pk),
                      headers={'Content-Type': 'application/octet-stream'},
                      verify=str(context.cert_path.resolve()),
                      timeout=60)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")


def prepare_code(src_path: Path,
                 service_context: Context,
                 patterns: Optional[List[str]] = None,
                 file_exceptions: Optional[List[str]] = None,
                 dir_exceptions: Optional[List[str]] = None) -> Path:
    """Tar and encrypt (if required) the app python code."""
    if service_context.code_protection == CodeProtection.Encrypted:

        log.debug("Encrypt code in %s to %s...", src_path,
                  service_context.encrypted_code_path)

        whitelist: Set[str] = {"requirements.txt"}

        encrypt_directory(
            dir_path=src_path,
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
