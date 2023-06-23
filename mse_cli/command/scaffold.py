"""mse_cli.command.scaffold module."""

import os
import shutil
from pathlib import Path

import pkg_resources
from jinja2 import Template
from mse_cli_core.conf import AppConf

from mse_cli.command.helpers import get_default, non_empty_string
from mse_cli.log import LOGGER as LOG
from mse_cli.model.user import UserConf


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "scaffold", help="create a new boilerplate MSE web application"
    )

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_name",
        type=non_empty_string,
        help="name of the MSE web application to create",
    )


# pylint: disable=too-many-locals
def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.from_toml()
    conn = user_conf.get_connection()

    config = get_default(conn=conn)

    project_dir = Path(os.getcwd()) / args.app_name

    # Copy the template files
    shutil.copytree(pkg_resources.resource_filename("mse_cli", "template"), project_dir)

    template_conf_file = project_dir / "mse.toml.template"
    conf_file = template_conf_file.with_suffix("")  # Remove .template extension

    # Initialize the configuration file
    tm = Template(template_conf_file.read_text())
    content = tm.render(
        name=args.app_name,
        docker=config.docker,
        project=config.project,
        hardware=config.hardware,
    )
    conf_file.write_text(content)
    template_conf_file.unlink()

    app_conf = AppConf.load(conf_file)
    cloud_conf = app_conf.cloud_or_raise()

    # Initialize the python code file
    code_dir = project_dir / cloud_conf.location
    template_code_file = code_dir / (app_conf.python_module + ".py.template")
    code_file = template_code_file.with_suffix("")

    tm = Template(template_code_file.read_text())
    content = tm.render(
        app=app_conf.python_variable,
        healthcheck_endpoint=app_conf.healthcheck_endpoint,
    )
    code_file.write_text(content)
    template_code_file.unlink()

    # Initialize the .mseignore
    code_dir = project_dir / cloud_conf.location
    ignore_file: Path = code_dir / "dotmseignore"
    ignore_file.rename(code_dir / ".mseignore")

    # Initialize the pytest code files
    pytest_dir = project_dir / "tests"
    template_pytest_file = pytest_dir / "conftest.py.template"
    pytest_file = template_pytest_file.with_suffix("")

    tm = Template(template_pytest_file.read_text())
    content = tm.render()
    pytest_file.write_text(content)
    template_pytest_file.unlink()

    pytest_dir = project_dir / "tests"
    template_pytest_file = pytest_dir / "test_app.py.template"
    pytest_file = template_pytest_file.with_suffix("")

    tm = Template(template_pytest_file.read_text())
    content = tm.render(healthcheck_endpoint=app_conf.healthcheck_endpoint)
    pytest_file.write_text(content)
    template_pytest_file.unlink()

    LOG.success(  # type: ignore
        "An example app has been generated in the directory: %s/", args.app_name
    )
    LOG.warning("You can configure your MSE application in: %s", conf_file)
    LOG.info(
        "You can now test it locally from the '%s/' directory using: \n\n\tmse test\n\n"
        "then, in another terminal:\n\n\tpytest\n",
        args.app_name,
    )
    LOG.advice(  # type: ignore
        "Or deploy it from the '%s/' directory using: \n\n\tmse deploy\n", args.app_name
    )
    LOG.info("Refer to the '%s/README.md' for more details", args.app_name)
