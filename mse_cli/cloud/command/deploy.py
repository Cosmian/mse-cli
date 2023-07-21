"""mse_cli.cloud.command.deploy module."""

from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

import requests

from mse_cli import MSE_DOC_SECURITY_MODEL_URL
from mse_cli.cloud.api.app import new
from mse_cli.cloud.api.auth import Connection
from mse_cli.cloud.api.types import App, AppStatus, SSLCertificateOrigin
from mse_cli.cloud.command.helpers import (
    exists_in_project,
    get_app,
    get_client_docker,
    get_enclave_resources,
    get_project_from_name,
    prepare_code,
    stop_app,
    verify_app,
)
from mse_cli.cloud.model.context import Context
from mse_cli.cloud.model.user import UserConf
from mse_cli.color import COLOR, ColorKind
from mse_cli.core.bootstrap import ConfigurationPayload, configure_app
from mse_cli.core.clock_tick import ClockTick
from mse_cli.core.conf import AppConf, AppConfParsingOption
from mse_cli.core.spinner import Spinner
from mse_cli.error import (
    AppContainerBadState,
    AppContainerError,
    BadApplicationInput,
    UnexpectedResponse,
)
from mse_cli.log import LOGGER as LOG


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

    parser.add_argument(
        "--workspace",
        type=Path,
        required=False,
        help="directory to write the temporary files",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        required=False,
        default=24 * 60,
        help="stop the deployment if the application does not "
        "respond after a delay (in min). (Default: 1440 min)",
    )

    parser.set_defaults(func=run)


# pylint: disable=too-many-branches,too-many-statements
def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.load()
    app_conf = AppConf.load(
        path=args.path,
        option=AppConfParsingOption.UseInsecureCloud
        if args.untrusted_ssl
        else AppConfParsingOption.All,
    )
    cloud_conf = app_conf.cloud_or_raise()
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
            COLOR.render(ColorKind.LINK_START),
            MSE_DOC_SECURITY_MODEL_URL,
            COLOR.render(ColorKind.LINK_MID),
            sec_doc_text,
            COLOR.render(ColorKind.LINK_END),
        )
        if cloud_conf.ssl:
            LOG.warning("SSL conf paragraph is ignored.%s")

    (enclave_size, cores) = get_enclave_resources(conn, cloud_conf.hardware)
    context = Context.from_app_conf(app_conf, workspace=args.workspace)
    LOG.info("Temporary workspace is: %s", context.workspace)

    LOG.info("Encrypting your source code...")
    (tar_path, nonces) = prepare_code(cloud_conf.code, context)

    LOG.info(
        "Deploying your app '%s' with %dM memory and %.2f CPU cores...",
        app_conf.name,
        enclave_size,
        cores,
    )
    app = deploy_app(conn, app_conf, tar_path)

    LOG.advice(  # type: ignore
        "To follow the app creation, you can run: \n\n\tmse cloud logs %s\n", app.id
    )

    app = wait_app_creation(conn, app.id, args.timeout)

    context.run(
        app.id,
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
            COLOR.render(ColorKind.LINK_START),
            MSE_DOC_SECURITY_MODEL_URL,
            COLOR.render(ColorKind.LINK_MID),
            sec_doc_text,
            COLOR.render(ColorKind.LINK_END),
        )

    verify_app(
        None if args.no_verify else context,
        app.config_domain_name,
        context.config_cert_path,
    )

    LOG.info("Sending secret key and decrypting the application code...")
    decrypt_private_data(
        context,
        ssl_private_key=cloud_conf.ssl.private_key_data if cloud_conf.ssl else None,
        app_secrets=cloud_conf.secrets_data,
    )

    app = wait_app_start(conn, app.id, args.timeout)

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
        "mse cloud context --export %s\n",
        app.id,
    )

    if app.ssl_certificate_origin == SSLCertificateOrigin.Self:
        LOG.advice(  # type: ignore
            "You can now test your application doing `mse cloud test` "
            "or use it as follow: \n\n\tcurl https://%s%s --cacert %s\n",
            app.domain_name,
            app.healthcheck_endpoint,
            context.config_cert_path,
        )
    else:
        LOG.advice(  # type: ignore
            "You can now test your application doing `mse cloud test` "
            "or use it as follow: \n\n\tcurl https://%s%s\n",
            app.domain_name,
            app.healthcheck_endpoint,
        )

    # Clean up the workspace
    # LOG.info("Cleaning up the temporary workspace...")
    # shutil.rmtree(context.workspace)


def wait_app_start(conn: Connection, app_id: UUID, timeout: int) -> App:
    """Wait for the app to be started."""
    with Spinner("Waiting for your application to be ready... "):
        clock = ClockTick(
            period=3,
            timeout=timeout * 60,
            message="MSE is at high capacity right now! Try again later.",
        )
        while clock.tick():
            app = get_app(conn=conn, app_id=app_id)

            if app.status == AppStatus.Spawning:
                raise AppContainerBadState(
                    "The app shoudn't be in the state spawning at this stage..."
                )
            if app.status == AppStatus.Running:
                break
            if app.status == AppStatus.OnError:
                raise AppContainerError(
                    "The app creation stopped because an error occurred..."
                )
            if app.status == AppStatus.Stopped:
                raise AppContainerError(
                    "The app creation stopped because it has been "
                    "stopped in the meantime..."
                )

    return app


def check_app_conf(conn: Connection, app_conf: AppConf, force: bool = False) -> bool:
    """Check app conf: project exist, app name exist, etc."""
    # Check that the project exists
    cloud_conf = app_conf.cloud_or_raise()
    project = get_project_from_name(conn, cloud_conf.project)
    if not project:
        raise BadApplicationInput(f"Project {cloud_conf.project} does not exist")

    # Check that a same name application is not running yet
    app = exists_in_project(
        conn,
        project.id,
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
            stop_app(conn, app.id)

    if not (
        cloud_conf.code / (app_conf.python_module.replace(".", "/") + ".py")
    ).exists():
        raise FileNotFoundError(
            f"Flask module '{app_conf.python_module}' "
            f"not found in directory: {cloud_conf.code}!"
        )

    return True


def deploy_app(conn: Connection, app_conf: AppConf, tar_path: Path) -> App:
    """Deploy the app to an MSE node."""
    r: requests.Response = new(conn=conn, conf=app_conf, code_tar_path=tar_path)

    if not r.ok:
        raise UnexpectedResponse(r.text)

    return App.from_dict(r.json())


def wait_app_creation(conn: Connection, app_id: UUID, timeout: int) -> App:
    """Wait for the app to be deployed."""
    with Spinner(f"Creating app {app_id}... "):
        clock = ClockTick(
            period=3,
            timeout=timeout * 60,
            message="MSE is at high capacity right now! Try again later.",
        )
        while clock.tick():
            app = get_app(conn=conn, app_id=app_id)

            if app.status == AppStatus.Initializing:
                break
            if app.status == AppStatus.Running:
                raise AppContainerBadState(
                    "The app shouldn't be in the state running at this stage..."
                )
            if app.status == AppStatus.OnError:
                raise AppContainerError(
                    "The app creation stopped because an error occurred..."
                )
            if app.status == AppStatus.Stopped:
                raise AppContainerError(
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

    data = ConfigurationPayload(
        app_id=context.instance.id,
        secrets=app_secrets,
        sealed_secrets=None,
        code_secret_key=context.config.code_secret_key,
        ssl_private_key=ssl_private_key,
    )

    configure_app(
        f"https://{context.instance.config_domain_name}",
        data.payload(),
        str(context.config_cert_path),
    )
