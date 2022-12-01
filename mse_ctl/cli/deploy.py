"""Deploy subparser definition."""

import time
from pathlib import Path
from typing import List, Optional, Set
from uuid import UUID

import requests
from mse_lib_crypto.xsalsa20_poly1305 import encrypt_directory

from mse_ctl.api.app import new
from mse_ctl.api.auth import Connection
from mse_ctl.api.types import App, AppStatus, SSLCertificateOrigin
from mse_ctl.cli.helpers import (compute_mr_enclave, exists_in_project, get_app,
                                 get_certificate, get_enclave_resources,
                                 get_project_from_name, stop_app, verify_app)
from mse_ctl.conf.app import AppConf
from mse_ctl.conf.context import Context
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.fs import tar


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("deploy",
                                   help="Deploy the application from the "
                                   "current directory into a MSE node")

    parser.add_argument(
        '--path',
        type=Path,
        required=False,
        metavar='path/to/mse/app/mse.toml',
        help='Path to the mse app to deploy (current directory if not set)')

    parser.set_defaults(func=run)


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    app_conf = AppConf.from_toml(path=args.path)
    conn = user_conf.get_connection()

    if not check_app_conf(conn, app_conf):
        return

    (enclave_size, cores) = get_enclave_resources(conn, app_conf.plan)
    context = Context.from_app_conf(app_conf)
    log.info("Temporary workspace is: %s", context.workspace)

    log.info("Encrypting your source code...")
    tar_path = prepare_code(app_conf.code.location, context)

    log.info("Deploying your app...")
    app = deploy_app(conn, app_conf, tar_path)

    log.info("App creating for %s:%s with %dM EPC memory and %.2f CPU cores...",
             app.name, app.version, enclave_size, cores)
    app = wait_app_creation(conn, app.uuid)

    context.run(app.uuid, enclave_size, app.config_domain_name,
                app.docker_version, app.expires_at, app.ssl_certificate_origin)

    log.info("✅%s App created with uuid: %s%s", bcolors.OKGREEN, app.uuid,
             bcolors.ENDC)

    selfsigned_cert = get_certificate(app.config_domain_name)
    context.config_cert_path.write_text(selfsigned_cert)

    log.info("Checking app trustworthiness...")
    mr_enclave = compute_mr_enclave(context, tar_path)
    log.info("The code fingerprint is %s", mr_enclave)
    verify_app(mr_enclave, selfsigned_cert)
    log.info("Verification: %ssuccess%s", bcolors.OKGREEN, bcolors.ENDC)

    if app.ssl_certificate_origin == SSLCertificateOrigin.Self:
        log.info("✅%s The verified certificate has been saved at: %s%s",
                 bcolors.OKGREEN, context.config_cert_path, bcolors.ENDC)

    log.info("Unsealing your private data from your mse instance...")
    unseal_private_data(
        context,
        ssl_private_key=app_conf.ssl.private_key if app_conf.ssl else None)

    log.info("Waiting for application to be ready...")
    app = wait_app_start(conn, app.uuid)

    log.info("Your application is now fully deployed and started...")
    log.info("✅%s It's now ready to be used on https://%s until %s%s",
             bcolors.OKGREEN, app.domain_name, app.expires_at, bcolors.ENDC)

    context.save()

    log.info("The context of this creation has been saved at: %s", context.path)


def wait_app_start(conn: Connection, uuid: UUID) -> App:
    """Wait for the app to be started."""
    while True:
        time.sleep(3)
        app = get_app(conn=conn, uuid=uuid)

        if app.status == AppStatus.Spawning:
            raise Exception(
                "The app shoudn't be in the state spawning at this stage...")
        if app.status == AppStatus.Running:
            break
        if app.status == AppStatus.OnError:
            raise Exception(
                "The app creation stopped because an error occured...")
        if app.status == AppStatus.Deleted:
            raise Exception("The app creation stopped because it "
                            "has been deleted in the meantime...")
        if app.status == AppStatus.Stopped:
            raise Exception("The app creation stopped because it "
                            "has been stopped in the meantime...")

    return app


def check_app_conf(conn: Connection, app_conf: AppConf) -> bool:
    """Check app conf: project exist, app name exist, etc."""
    # Check that the project exists
    project = get_project_from_name(conn, app_conf.project)
    if not project:
        raise Exception(f"Project {app_conf.project} does not exist")

    # Check that a same name application is not running yet
    app = exists_in_project(conn, project.uuid, app_conf.name, [
        AppStatus.Spawning,
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

    if not (app_conf.code.location /
            (app_conf.python_module.replace(".", "/") + ".py")).exists():
        raise FileNotFoundError(
            f"Flask module '{app_conf.python_module}' "
            f"not found in directory: {app_conf.code.location}!")

    return True


def deploy_app(conn: Connection, app_conf: AppConf, tar_path: Path) -> App:
    """Deploy the app to a mse node."""
    r: requests.Response = new(conn=conn, conf=app_conf, code_tar_path=tar_path)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    return App.from_json_dict(r.json())


def wait_app_creation(conn: Connection, uuid: UUID) -> App:
    """Wait for the app to be deployed."""
    while True:
        time.sleep(3)
        app = get_app(conn=conn, uuid=uuid)

        if app.status == AppStatus.Initializing:
            break
        if app.status == AppStatus.Running:
            raise Exception(
                "The app shoudn't be in the state running at this stage...")
        if app.status == AppStatus.OnError:
            raise Exception(
                "The app creation stopped because an error occured...")
        if app.status == AppStatus.Deleted:
            raise Exception("The app creation stopped because it "
                            "has been deleted in the meantime...")
        if app.status == AppStatus.Stopped:
            raise Exception("The app creation stopped because it "
                            "has been stopped in the meantime...")

    return app


def unseal_private_data(context: Context,
                        ssl_private_key: Optional[str] = None):
    """Send the ssl private key and the key which was used to encrypt the code."""
    assert context.instance

    data = {
        "code_sealed_key": context.config.code_sealed_key.hex(),
        "uuid": str(context.instance.id)
    }

    if ssl_private_key:
        data["ssl_private_key"] = ssl_private_key

    r = requests.post(url=f"https://{context.instance.config_domain_name}",
                      json=data,
                      headers={'Content-Type': 'application/json'},
                      verify=str(context.config_cert_path),
                      timeout=60)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")


def prepare_code(src_path: Path,
                 context: Context,
                 patterns: Optional[List[str]] = None,
                 file_exceptions: Optional[List[str]] = None,
                 dir_exceptions: Optional[List[str]] = None) -> Path:
    """Tar and encrypt (if required) the app python code."""
    log.debug("Encrypt code in %s to %s...", src_path,
              context.encrypted_code_path)

    whitelist: Set[str] = {"requirements.txt"}

    encrypt_directory(
        dir_path=src_path,
        patterns=(["*"] if patterns is None else patterns),
        key=context.config.code_sealed_key,
        exceptions=(list(whitelist) if file_exceptions is None else
                    list(set(file_exceptions) | whitelist)),
        dir_exceptions=([] if dir_exceptions is None else dir_exceptions),
        out_dir_path=context.encrypted_code_path)

    tar_path = tar(dir_path=context.encrypted_code_path,
                   tar_path=context.tar_code_path)

    log.debug("Tar encrypted code in '%s'", tar_path.name)

    return tar_path
