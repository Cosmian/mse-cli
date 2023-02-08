"""Test error scenari on cli/*.py."""

import os
from argparse import Namespace
from pathlib import Path

import pytest
from conftest import capture_logs

from mse_cli.command.context import run as run_context
from mse_cli.command.deploy import run as run_deploy
from mse_cli.command.list_all import run as run_list
from mse_cli.command.logs import run as run_logs
from mse_cli.command.scaffold import run as run_scaffold
from mse_cli.command.status import run as run_status
from mse_cli.command.stop import run as run_stop
from mse_cli.command.verify import run as run_verify


@pytest.mark.slow
def test_status_bad_uuid(cmd_log):
    """Test status with the error: valid id but no exists."""
    with pytest.raises(Exception) as exception:
        run_status(
            Namespace(**{
                "app_uuid": "00000000-0000-0000-0000-000000000000",
            }))

    assert "Cannot find the app with UUID " in str(exception.value)


@pytest.mark.slow
def test_logs_bad_uuid(cmd_log):
    """Test status with the error: valid id but no exists."""
    with pytest.raises(Exception) as exception:
        run_logs(
            Namespace(**{
                "app_uuid": "00000000-0000-0000-0000-000000000000",
            }))

    assert "Cannot find the app with UUID " in str(exception.value)


@pytest.mark.slow
def test_scaffold_bad_name(cmd_log):
    """Test scaffold with the error: bad name."""
    with pytest.raises(Exception) as exception:
        run_scaffold(Namespace(**{"app_name": ""}))

    assert "File exists" in str(exception.value)


@pytest.mark.slow
def test_list_bad_project_name(cmd_log):
    """Test list with the error: project name does not exist."""
    with pytest.raises(Exception) as exception:
        run_list(Namespace(**{"project_name": "notexist", "all": False}))

    assert "Project notexist does not exist" in str(exception.value)


@pytest.mark.slow
def test_context_bad_id(cmd_log):
    """Test context with the error: id does not exist."""
    with pytest.raises(FileNotFoundError) as exception:
        run_context(
            Namespace(
                **{
                    "list": False,
                    "remove": "00000000-0000-0000-0000-000000000000",
                    "purge": False,
                    "export": None
                }))

    assert "No such file or directory" in str(exception.value)

    with pytest.raises(FileNotFoundError) as exception:
        run_context(
            Namespace(
                **{
                    "list": False,
                    "remove": None,
                    "purge": False,
                    "export": "00000000-0000-0000-0000-000000000000"
                }))

    assert "Can't find context for UUID" in str(exception.value)


@pytest.mark.slow
def test_stop_bad_uuid(cmd_log):
    """Test stop with the error: valid id but no exists."""
    with pytest.raises(Exception) as exception:
        run_stop(
            Namespace(**{
                "app_uuid": "00000000-0000-0000-0000-000000000000",
            }))

    assert "Cannot find the app with UUID " in str(exception.value)


@pytest.mark.slow
def test_verify_bad_domain(cmd_log):
    """Test verify with the error: valid domain but no exists."""
    run_verify(
        Namespace(
            **{
                "fingerprint": None,
                "context": None,
                "code": None,
                "domain_name": f"notexist.{os.getenv('MSE_TEST_DOMAIN_NAME')}"
            }))
    output = capture_logs(cmd_log)
    assert "Are you sure the application is still running?" in output

    run_verify(
        Namespace(
            **{
                "fingerprint": None,
                "context": None,
                "code": None,
                "domain_name": f"notexist.app"
            }))
    output = capture_logs(cmd_log)
    assert "Are you sure the application is still running?" in output


@pytest.mark.slow
def test_deploy_non_free(cmd_log):
    """Test deploy with the error: non free plan but no payment."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path":
                        Path(__file__).parent / "data" / "non_free_plan.toml",
                    "y":
                        False,
                    "no_verify":
                        False,
                    "untrusted_ssl":
                        False
                }))

    assert "Cannot find the plan with name 'green'" in str(exception.value)


@pytest.mark.slow
def test_deploy_bad_projet_name(cmd_log):
    """Test deploy with the error: project name does not exist."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path":
                        Path(__file__).parent / "data" /
                        "bad_project_name.toml",
                    "y":
                        False,
                    "no_verify":
                        False,
                    "untrusted_ssl":
                        False
                }))

    assert "Project notexist does not exist" in str(exception.value)


@pytest.mark.slow
def test_deploy_bad_app(cmd_log):
    """Test deploy with the error: bad python app."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path":
                        Path(__file__).parent / "data" /
                        "bad_python_application.toml",
                    "y":
                        False,
                    "no_verify":
                        False,
                    "untrusted_ssl":
                        False
                }))

    assert "Flask module 'app' not found in directory" in str(exception.value)


@pytest.mark.slow
def test_deploy_bad_docker(cmd_log):
    """Test deploy with the error: bad docker name."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path": Path(__file__).parent / "data" / "bad_docker.toml",
                    "y": False,
                    "no_verify": False,
                    "untrusted_ssl": False
                }))

    assert "Docker 'ghcr.io/cosmian/mse-pytorch:notexist' is not approved or supported yet." in str(
        exception.value)


@pytest.mark.slow
def test_deploy_latest_docker(cmd_log):
    """Test deploy with the error: latest docker name."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path":
                        Path(__file__).parent / "data" /
                        "bad_docker_latest.toml",
                    "y":
                        False,
                    "no_verify":
                        False,
                    "untrusted_ssl":
                        False
                }))

    assert "You shouldn\'t use latest tag for the docker image" in str(
        exception.value)
