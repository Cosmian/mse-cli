"""Test error scenari on cli/*.py."""

import os
from argparse import Namespace
from pathlib import Path

import pytest

from mse_cli.cloud.command.context import run as run_context
from mse_cli.cloud.command.deploy import run as run_deploy
from mse_cli.cloud.command.list_all import run as run_list
from mse_cli.cloud.command.logs import run as run_logs
from mse_cli.cloud.command.scaffold import run as run_scaffold
from mse_cli.cloud.command.status import run as run_status
from mse_cli.cloud.command.stop import run as run_stop
from mse_cli.cloud.command.verify import run as run_verify


@pytest.mark.cloud
def test_status_bad_uuid():
    """Test status with the error: valid id but no exists."""
    with pytest.raises(Exception) as exception:
        run_status(
            Namespace(
                **{
                    "app_id": "00000000-0000-0000-0000-000000000000",
                }
            )
        )

    assert "Cannot find the app with id " in str(exception.value)


@pytest.mark.cloud
def test_logs_bad_uuid():
    """Test status with the error: valid id but no exists."""
    with pytest.raises(Exception) as exception:
        run_logs(
            Namespace(
                **{
                    "app_id": "00000000-0000-0000-0000-000000000000",
                }
            )
        )

    assert "Cannot find the app with id " in str(exception.value)


@pytest.mark.cloud
def test_scaffold_bad_name():
    """Test scaffold with the error: bad name."""
    with pytest.raises(Exception) as exception:
        run_scaffold(Namespace(**{"app_name": ""}))

    assert "File exists" in str(exception.value)


@pytest.mark.cloud
def test_list_bad_project_name():
    """Test list with the error: project name does not exist."""
    with pytest.raises(Exception) as exception:
        run_list(Namespace(**{"project_name": "notexist", "all": False}))

    assert "Project notexist does not exist" in str(exception.value)


@pytest.mark.cloud
def test_context_bad_id():
    """Test context with the error: id does not exist."""
    with pytest.raises(FileNotFoundError) as exception:
        run_context(
            Namespace(
                **{
                    "list": False,
                    "remove": "00000000-0000-0000-0000-000000000000",
                    "purge": False,
                    "export": None,
                }
            )
        )

    assert "No such file or directory" in str(exception.value)

    with pytest.raises(FileNotFoundError) as exception:
        run_context(
            Namespace(
                **{
                    "list": False,
                    "remove": None,
                    "purge": False,
                    "export": "00000000-0000-0000-0000-000000000000",
                }
            )
        )

    assert "Can't find context for UUID" in str(exception.value)


@pytest.mark.cloud
def test_stop_bad_uuid():
    """Test stop with the error: valid id but no exists."""
    with pytest.raises(Exception) as exception:
        run_stop(
            Namespace(
                **{
                    "app_id": ["00000000-0000-0000-0000-000000000000"],
                }
            )
        )

    assert "Cannot find the app with id " in str(exception.value)


@pytest.mark.cloud
def test_verify_bad_domain(tmp_path):
    """Test verify with the error: valid domain but no exists."""
    with pytest.raises(Exception) as exception:
        run_verify(
            Namespace(
                **{
                    "fingerprint": None,
                    "context": None,
                    "code": None,
                    "domain_name": f"notexist.{os.getenv('MSE_TEST_DOMAIN_NAME')}",
                    "workspace": tmp_path,
                }
            )
        )

    assert "Are you sure the application is still running?" in str(exception.value)

    with pytest.raises(Exception) as exception:
        run_verify(
            Namespace(
                **{
                    "fingerprint": None,
                    "context": None,
                    "code": None,
                    "domain_name": "notexist.app",
                    "workspace": tmp_path,
                }
            )
        )

    assert "Are you sure the application is still running?" in str(exception.value)


@pytest.mark.cloud
def test_deploy_non_free(tmp_path):
    """Test deploy with the error: non free plan but no payment."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path": Path(__file__).parent / "data" / "non_free_plan.toml",
                    "y": False,
                    "no_verify": False,
                    "untrusted_ssl": False,
                    "workspace": tmp_path,
                    "timeout": 15,
                }
            )
        )

    assert (
        "Project `default` has not enough hardware available `64g-eu-001` to spawn app named `non_free`"
        in str(exception.value)
    )


@pytest.mark.cloud
def test_deploy_bad_projet_name(tmp_path):
    """Test deploy with the error: project name does not exist."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path": Path(__file__).parent / "data" / "bad_project_name.toml",
                    "y": False,
                    "no_verify": False,
                    "untrusted_ssl": False,
                    "workspace": tmp_path,
                    "timeout": 15,
                }
            )
        )

    assert "Project notexist does not exist" in str(exception.value)


@pytest.mark.cloud
def test_deploy_bad_app(tmp_path):
    """Test deploy with the error: bad python app."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path": Path(__file__).parent
                    / "data"
                    / "bad_python_application.toml",
                    "y": False,
                    "no_verify": False,
                    "untrusted_ssl": False,
                    "workspace": tmp_path,
                    "timeout": 15,
                }
            )
        )

    assert "Flask module 'app' not found in directory" in str(exception.value)


@pytest.mark.cloud
def test_deploy_bad_docker(tmp_path):
    """Test deploy with the error: bad docker name."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path": Path(__file__).parent / "data" / "bad_docker.toml",
                    "y": False,
                    "no_verify": False,
                    "untrusted_ssl": False,
                    "workspace": tmp_path,
                    "timeout": 15,
                }
            )
        )

    assert (
        "Docker `ghcr.io/cosmian/mse-pytorch:notexist` is not approved or supported yet."
        in str(exception.value)
    )


@pytest.mark.cloud
def test_deploy_latest_docker(tmp_path):
    """Test deploy with the error: latest docker name."""
    with pytest.raises(Exception) as exception:
        run_deploy(
            Namespace(
                **{
                    "path": Path(__file__).parent / "data" / "bad_docker_latest.toml",
                    "y": False,
                    "no_verify": False,
                    "untrusted_ssl": False,
                    "workspace": tmp_path,
                    "timeout": 15,
                }
            )
        )

    assert "You shouldn't use latest tag for the docker image" in str(exception.value)
