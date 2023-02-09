"""mse_cli.command.deploy module."""

from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

import requests

from mse_cli import MSE_DOC_SECURITY_MODEL_URL
from mse_cli.api.app import new
from mse_cli.api.auth import Connection
from mse_cli.api.types import App, AppStatus, SSLCertificateOrigin
from mse_cli.command.helpers import (
    compute_mr_enclave,
    exists_in_project,
    get_app,
    get_certificate,
    get_client_docker,
    get_enclave_resources,
    get_project_from_name,
    prepare_code,
    stop_app,
    verify_app,
)
from mse_cli.conf.app import AppConf
from mse_cli.conf.context import Context
from mse_cli.conf.user import UserConf
from mse_cli.log import LOGGER as LOG
from mse_cli.utils.clock_tick import ClockTick
from mse_cli.utils.color import bcolors
from mse_cli.utils.spinner import Spinner


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "deploy", help="deploy an ASGI web application to MSE"
    )

    parser.add_argument(
        "--path",
        type=Path,
        required=False,
        metavar="FILE",
        help="path to the MSE toml config file to deploy "
        "(if not in the current directory)",
    )

    parser.add_argument(
        "-y",
        action="store_true",
        help="force to stop the application if it already exists",
    )

    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="speed up the deployment by skipping the app trustworthiness check",
    )

    parser.add_argument(
        "--untrusted-ssl",
        action="store_true",
        help="use operator ssl certificates which is unsecure for production",
    )

    parser.set_defaults(func=run)


# pylint: disable=too-many-branches,too-many-statements
def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    app_conf = AppConf.from_toml(path=args.path, ignore_ssl=args.untrusted_ssl)
    conn = user_conf.get_connection()

    if not args.no_verify:
        # Check docker daemon is running
        _ = get_client_docker()

    if not check_app_conf(conn, app_conf, args.y):
        return

    sec_doc_text = "Security Model documentation"

    if args.untrusted_ssl:
        LOG.warning(
            "This app runs in untrusted-ssl mode with an operator certificate. "
            "The operator may access all communications with the app. "
            "Read %s%s%s%s%s for more details.",
            bcolors.LINK_START,
            MSE_DOC_SECURITY_MODEL_URL,
            bcolors.LINK_MID,
            sec_doc_text,
            bcolors.LINK_END,
        )
        if app_conf.ssl:
            LOG.warning("SSL conf paragraph is ignored.%s")

    (enclave_size, cores) = get_enclave_resources(conn, app_conf.resource)
    context = Context.from_app_conf(app_conf)
    LOG.info("Temporary workspace is: %s", context.workspace)

    LOG.info("Encrypting your source code...")
    (tar_path, nonces) = prepare_code(app_conf.code.location, context)

    LOG.info(
        "Deploying your app '%s' with %dM memory and %.2f CPU cores...",
        app_conf.name,
        enclave_size,
        cores,
    )
    app = deploy_app(conn, app_conf, tar_path)

    LOG.advice(  # type: ignore
        "To follow the app creation, you can run: \n\n\tmse logs %s\n", app.uuid
    )

    app = wait_app_creation(conn, app.uuid)

    context.run(
        app.uuid,
        enclave_size,
        app.config_domain_name,
        app.expires_at,
        app.ssl_certificate_origin,
        nonces,
    )

    LOG.success("App created!")  # type: ignore

    if app.ssl_certificate_origin == SSLCertificateOrigin.Owner:
        LOG.warning(
            "This app runs with an app owner certificate. "
            "The app provider may decrypt all communications with the app. "
            "Read %s%s%s%s%s for more details.",
            bcolors.LINK_START,
            MSE_DOC_SECURITY_MODEL_URL,
            bcolors.LINK_MID,
            sec_doc_text,
            bcolors.LINK_END,
        )

    selfsigned_cert = get_certificate(app.config_domain_name)
    context.config_cert_path.write_text(selfsigned_cert)

    if not args.no_verify:
        with Spinner("Checking app trustworthiness... "):
            mr_enclave = compute_mr_enclave(context, tar_path)

        LOG.info("The code fingerprint is %s", mr_enclave)
        verify_app(mr_enclave, selfsigned_cert)
        LOG.success("Verification success")  # type: ignore

        if app.ssl_certificate_origin == SSLCertificateOrigin.Self:
            LOG.info(
                "The verified certificate has been saved at: %s",
                context.config_cert_path,
            )
    else:
        LOG.warning(
            "App trustworthiness checking skipped. The app integrity has "
            "not been checked and shouldn't be used in production mode!"
        )

    LOG.info("Sending secret key and decrypting the application code...")
    decrypt_private_data(
        context,
        ssl_private_key=app_conf.ssl.private_key_data if app_conf.ssl else None,
        app_secrets=app_conf.code.secrets_data,
    )

    app = wait_app_start(conn, app.uuid)

    LOG.success(  # type: ignore
        "Your application is now deployed and ready to be used on https://%s until %s",
        app.domain_name,
        app.expires_at.astimezone(),
    )
    LOG.info(
        "The application will be automatically stopped after this date "
        "(see the documentation for more details)."
    )

    context.save()

    LOG.advice(  # type: ignore
        "The context of this creation can be retrieved using: \n\n\t"
        "mse context --export %s\n",
        app.uuid,
    )

    if app.ssl_certificate_origin == SSLCertificateOrigin.Self:
        LOG.advice(  # type: ignore
            "You can now test your application: \n\n\tcurl https://%s%s "
            "--cacert %s\n",
            app.domain_name,
            app.healthcheck_endpoint,
            context.config_cert_path,
        )
    else:
        LOG.advice(  # type: ignore
            "You can now test your application: \n\n\tcurl https://%s%s\n",
            app.domain_name,
            app.healthcheck_endpoint,
        )


def wait_app_start(conn: Connection, uuid: UUID) -> App:
    """Wait for the app to be started."""
    with Spinner("Waiting for your application to be ready... "):
        clock = ClockTick(
            period=3,
            timeout=5 * 60,
            message="MSE is at high capacity right now! Try again later.",
        )
        while clock.tick():
            app = get_app(conn=conn, uuid=uuid)

            if app.status == AppStatus.Spawning:
                raise Exception(
                    "The app shoudn't be in the state spawning at this stage..."
                )
            if app.status == AppStatus.Running:
                break
            if app.status == AppStatus.OnError:
                raise Exception("The app creation stopped because an error occurred...")
            if app.status == AppStatus.Stopped:
                raise Exception(
                    "The app creation stopped because it has been "
                    "stopped in the meantime..."
                )

    return app


def check_app_conf(conn: Connection, app_conf: AppConf, force: bool = False) -> bool:
    """Check app conf: project exist, app name exist, etc."""
    # Check that the project exists
    project = get_project_from_name(conn, app_conf.project)
    if not project:
        raise Exception(f"Project {app_conf.project} does not exist")

    # Check that a same name application is not running yet
    app = exists_in_project(
        conn,
        project.uuid,
        app_conf.name,
        [
            AppStatus.Spawning,
            AppStatus.Initializing,
            AppStatus.Running,
        ],
    )

    if app:
        LOG.info(
            "An application with the same name in this project is already running..."
        )

        if not force:
            answer = input("Would you like to replace it [yes/no]? ")
            if answer.lower() not in ["y", "yes"]:
                LOG.info("Deployment has been canceled!")
                LOG.info("Please rename your application")
                return False

        with Spinner("Stopping the previous app... "):
            stop_app(conn, app.uuid)

    if not (
        app_conf.code.location / (app_conf.python_module.replace(".", "/") + ".py")
    ).exists():
        raise FileNotFoundError(
            f"Flask module '{app_conf.python_module}' "
            f"not found in directory: {app_conf.code.location}!"
        )

    return True


def deploy_app(conn: Connection, app_conf: AppConf, tar_path: Path) -> App:
    """Deploy the app to an MSE node."""
    r: requests.Response = new(conn=conn, conf=app_conf, code_tar_path=tar_path)

    if not r.ok:
        raise Exception(r.text)

    return App.from_dict(r.json())


def wait_app_creation(conn: Connection, uuid: UUID) -> App:
    """Wait for the app to be deployed."""
    with Spinner(f"Creating app {uuid}... "):
        clock = ClockTick(
            period=3,
            timeout=5 * 60,
            message="MSE is at high capacity right now! Try again later.",
        )
        while clock.tick():
            app = get_app(conn=conn, uuid=uuid)

            if app.status == AppStatus.Initializing:
                break
            if app.status == AppStatus.Running:
                raise Exception(
                    "The app shouldn't be in the state running at this stage..."
                )
            if app.status == AppStatus.OnError:
                raise Exception("The app creation stopped because an error occurred...")
            if app.status == AppStatus.Stopped:
                raise Exception(
                    "The app creation stopped because it "
                    "has been stopped in the meantime..."
                )

    return app


def decrypt_private_data(
    context: Context,
    ssl_private_key: Optional[str] = None,
    app_secrets: Optional[Dict[str, Any]] = None,
):
    """Send the ssl private key and the key which was used to encrypt the code."""
    assert context.instance

    data: Dict[str, Any] = {
        "code_secret_key": context.config.code_secret_key.hex(),
        "uuid": str(context.instance.id),
    }

    if ssl_private_key:
        data["ssl_private_key"] = ssl_private_key

    if app_secrets:
        data["app_secrets"] = app_secrets

    r = requests.post(
        url=f"https://{context.instance.config_domain_name}",
        json=data,
        headers={"Content-Type": "application/json"},
        verify=str(context.config_cert_path),
        timeout=60,
    )

    if not r.ok:
        raise Exception(r.text)
