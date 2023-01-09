"""mse_cli.command.deploy module."""

from pathlib import Path
from typing import Optional
from uuid import UUID

import requests

from mse_cli.api.app import new
from mse_cli.api.auth import Connection
from mse_cli.api.types import App, AppStatus, SSLCertificateOrigin
from mse_cli.command.helpers import (compute_mr_enclave, exists_in_project,
                                     get_app, get_certificate,
                                     get_enclave_resources, get_client_docker,
                                     get_project_from_name, prepare_code,
                                     stop_app, verify_app)
from mse_cli.conf.app import AppConf
from mse_cli.conf.context import Context
from mse_cli.conf.user import UserConf
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.color import bcolors
from mse_cli.utils.spinner import Spinner


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("deploy",
                                   help="deploy an ASGI web application to MSE")

    parser.add_argument("--path",
                        type=Path,
                        required=False,
                        metavar="FILE",
                        help="path to the MSE toml config file to deploy "
                        "(if not in the current directory)")

    parser.add_argument(
        "--force",
        action="store_true",
        help="force to stop the application if it already exists")

    parser.add_argument(
        "--insecure",
        action="store_true",
        help="speed up the deployment by not verifying the app trustworthiness")

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    app_conf = AppConf.from_toml(path=args.path)
    conn = user_conf.get_connection()

    if not args.insecure:
        # Check docker daemon is running
        _ = get_client_docker()

    if not check_app_conf(conn, app_conf, args.force):
        return

    (enclave_size, cores) = get_enclave_resources(conn, app_conf.plan)
    context = Context.from_app_conf(app_conf)
    LOG.info("Temporary workspace is: %s", context.workspace)

    LOG.info("Encrypting your source code...")
    (tar_path, nonces) = prepare_code(app_conf.code.location, context)

    LOG.info("Deploying your app...")
    app = deploy_app(conn, app_conf, tar_path)

    LOG.info(
        "App %s creating for %s:%s with %dM EPC memory and %.2f CPU cores...",
        app.uuid, app.name, app.version, enclave_size, cores)
    app = wait_app_creation(conn, app.uuid)

    context.run(app.uuid, enclave_size, app.config_domain_name, app.expires_at,
                app.ssl_certificate_origin, nonces)

    LOG.info("✅%s App created!%s", bcolors.OKGREEN, bcolors.ENDC)

    if app.ssl_certificate_origin == SSLCertificateOrigin.Operator:
        LOG.info(
            "%sThis app runs in dev mode with an operator certificate. "
            "The operator may access all communications with the app. "
            "See Documentation > Security Model for more details.%s",
            bcolors.WARNING, bcolors.ENDC)
    elif app.ssl_certificate_origin == SSLCertificateOrigin.Owner:
        LOG.info(
            "%sThis app runs with an app owner certificate. "
            "The app provider may decrypt all communications with the app. "
            "See Documentation > Security Model for more details.%s",
            bcolors.WARNING, bcolors.ENDC)

    selfsigned_cert = get_certificate(app.config_domain_name)
    context.config_cert_path.write_text(selfsigned_cert)

    if not args.insecure:
        LOG.info("Checking app trustworthiness...")
        mr_enclave = compute_mr_enclave(context, tar_path)
        LOG.info("The code fingerprint is %s", mr_enclave)
        verify_app(mr_enclave, selfsigned_cert)
        LOG.info("Verification: %ssuccess%s", bcolors.OKGREEN, bcolors.ENDC)

        if app.ssl_certificate_origin == SSLCertificateOrigin.Self:
            LOG.info("✅%s The verified certificate has been saved at: %s%s",
                     bcolors.OKGREEN, context.config_cert_path, bcolors.ENDC)
    else:
        LOG.info(
            "%sApp trustworthiness checking skipped. This deployment is "
            "insecured and shouldn't be used in production mode!!!%s",
            bcolors.WARNING, bcolors.ENDC)

    LOG.info("Unsealing your private data from your mse instance...")
    unseal_private_data(
        context,
        ssl_private_key=app_conf.ssl.private_key if app_conf.ssl else None)

    LOG.info("Waiting for application to be ready...")
    app = wait_app_start(conn, app.uuid)

    LOG.info("Your application is now fully deployed and started...")
    LOG.info(
        "✅%s It's now ready to be used on https://%s until %s%s. "
        "The application will be automatically stopped after this date.",
        bcolors.OKGREEN, app.domain_name, app.expires_at.astimezone(),
        bcolors.ENDC)

    context.save()

    LOG.info(
        "The context of this creation can be retrieved using "
        "`mse context --export %s`", app.uuid)

    if app.ssl_certificate_origin == SSLCertificateOrigin.Self:
        LOG.info(
            "%sYou can now quickly test your application doing: `curl https://%s%s "
            "--cacert %s`%s", bcolors.OKBLUE, app.domain_name,
            app.health_check_endpoint, context.config_cert_path, bcolors.ENDC)
    else:
        LOG.info(
            "%sYou can now quickly test your application doing: `curl https://%s%s`%s",
            bcolors.OKBLUE, app.domain_name, app.health_check_endpoint,
            bcolors.ENDC)


def wait_app_start(conn: Connection, uuid: UUID) -> App:
    """Wait for the app to be started."""
    spinner = Spinner(3)
    while True:
        spinner.wait()
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

    spinner.reset()
    return app


def check_app_conf(conn: Connection,
                   app_conf: AppConf,
                   force: bool = False) -> bool:
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
        LOG.info(
            "An application with the same name in that project is already running..."
        )
        if force:
            LOG.info("Stopping the previous app (force mode enabled)...")
            stop_app(conn, app.uuid)
        else:
            answer = input("Would you like to replace it [yes/no]? ")
            if answer.lower() in ["y", "yes"]:
                LOG.info("Stopping the previous app...")
                stop_app(conn, app.uuid)
            else:
                LOG.info("Your deployment has been stopped!")
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

    return App.from_dict(r.json())


def wait_app_creation(conn: Connection, uuid: UUID) -> App:
    """Wait for the app to be deployed."""
    spinner = Spinner(3)
    while True:
        spinner.wait()

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

    spinner.reset()
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
                      headers={"Content-Type": "application/json"},
                      verify=str(context.config_cert_path),
                      timeout=60)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")
