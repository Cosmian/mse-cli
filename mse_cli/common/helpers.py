"""mse_cli.common.helpers module."""

import os
import shutil
from pathlib import Path
from typing import Optional

import pkg_resources
from jinja2 import Template
from mse_cli.cloud.api.types import DefaultAppConfig

from mse_cli.core.conf import AppConf, AppConfParsingOption
from mse_cli.home.model.package import (
    DEFAULT_CODE_DIR,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_TEST_DIR,
)
from mse_cli.log import LOGGER as LOG


def scaffold(app_name: str, cloud_config: Optional[DefaultAppConfig] = None) -> Path:
    """Run the subcommand."""
    project_dir = Path(os.getcwd()) / app_name

    # Copy the template files
    shutil.copytree(pkg_resources.resource_filename("mse_cli", "template"), project_dir)

    template_conf_file = project_dir / "mse.toml.template"
    conf_file = project_dir / DEFAULT_CONFIG_FILENAME

    # Initialize the configuration file
    tm = Template(template_conf_file.read_text())
    if cloud_config:
        content = tm.render(
            name=app_name,
            docker=cloud_config.docker,
            project=cloud_config.project,
            hardware=cloud_config.hardware,
        )
    else:
        content = tm.render(name=app_name)

    conf_file.write_text(content)
    template_conf_file.unlink()

    app_conf = AppConf.load(
        conf_file,
        option=AppConfParsingOption.All
        if cloud_config
        else AppConfParsingOption.SkipCloud,
    )

    # Initialize the python code file
    code_dir = project_dir / (
        app_conf.cloud.location if app_conf.cloud else DEFAULT_CODE_DIR
    )
    template_code_file = code_dir / (app_conf.python_module + ".py.template")
    code_file = template_code_file.with_suffix("")

    tm = Template(template_code_file.read_text())
    content = tm.render(
        app=app_conf.python_variable,
        mse_home=cloud_config is None,
        healthcheck_endpoint=app_conf.healthcheck_endpoint,
    )
    code_file.write_text(content)
    template_code_file.unlink()

    # Initialize the .mseignore
    ignore_file: Path = code_dir / "dotmseignore"
    ignore_file.rename(code_dir / ".mseignore")

    # Initialize the pytest code files
    pytest_dir = project_dir / DEFAULT_TEST_DIR
    template_pytest_file = pytest_dir / "conftest.py.template"
    pytest_file = template_pytest_file.with_suffix("")

    tm = Template(template_pytest_file.read_text())
    content = tm.render(
        mse_home=cloud_config is None,
    )
    pytest_file.write_text(content)
    template_pytest_file.unlink()

    pytest_dir = project_dir / DEFAULT_TEST_DIR
    template_pytest_file = pytest_dir / "test_app.py.template"
    pytest_file = template_pytest_file.with_suffix("")

    tm = Template(template_pytest_file.read_text())
    content = tm.render(
        mse_home=cloud_config is None,
        healthcheck_endpoint=app_conf.healthcheck_endpoint,
    )
    pytest_file.write_text(content)
    template_pytest_file.unlink()

    return conf_file
