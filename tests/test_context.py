"""Test conf/context.py."""

import filecmp
import os
from datetime import datetime
from pathlib import Path
from uuid import UUID

from mse_cli.cloud.api.types import SSLCertificateOrigin
from mse_cli.cloud.model.context import Context, ContextConf, ContextInstance
from mse_cli.core.conf import AppConf, CloudConf, SSLConf


def test_load():
    """Test `load` function."""
    toml = Path(__file__).parent / "data/context.toml"
    conf = Context.load(path=toml)

    ref_context_conf = Context(
        version="2.0",
        workspace=conf.workspace,
        config=ContextConf(
            name="helloworld",
            project="default",
            code_secret_key="a389f8baf2e03cebd445d99f03600b29ca259faa9a3964e529c03effef206135",
            docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
            python_application="app:app",
            ssl_app_certificate=(Path(__file__).parent / "data/cert.pem").read_text(),
            tests="/home/user/tests",
            tests_cmd="pytest",
            tests_requirements=[
                "intel-sgx-ra",
                "pytest==7.2.0",
            ],
        ),
        instance=ContextInstance(
            id="d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e",
            config_domain_name="demo.dev.cosmilink.com",
            enclave_size=1,
            expires_at=datetime.strptime(
                "2022-11-18 16:22:11.516125", "%Y-%m-%d %H:%M:%S.%f"
            ),
            ssl_certificate_origin=SSLCertificateOrigin.Owner,
            nonces={"app.py": "f33f4a1a1555660f9396aea7811b0ff7b0f19503a7485914"},
        ),
    )

    assert conf == ref_context_conf


def test_from_app_conf():
    """Test `from_app_conf` function."""
    ref_app_conf = AppConf(
        name="helloworld",
        python_application="app:app",
        healthcheck_endpoint="/",
        tests_cmd="pytest",
        tests_requirements=["intel-sgx-ra>=1.0.1,<1.1", "pytest==7.2.0"],
        cloud=CloudConf(
            project="default",
            hardware="4g-eu-001",
            code="/tmp/code",
            tests="/home/user/tests",
            docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
            ssl=SSLConf(
                domain_name="demo.dev.cosmilink.com",
                private_key=Path(__file__).parent / "data/key.pem",
                certificate=Path(__file__).parent / "data/cert.pem",
            ),
        ),
    )

    conf = Context.from_app_conf(conf=ref_app_conf)

    ref_context_conf = Context(
        version="2.0",
        workspace=conf.workspace,
        config=ContextConf(
            name="helloworld",
            project="default",
            code_secret_key=conf.config.code_secret_key,
            python_application="app:app",
            ssl_app_certificate=(Path(__file__).parent / "data/cert.pem").read_text(),
            docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
            tests_cmd="pytest",
            tests_requirements=["intel-sgx-ra>=1.0.1,<1.1", "pytest==7.2.0"],
            tests="/home/user/tests",
        ),
        instance=None,
    )

    assert conf == ref_context_conf


def test_run():
    """Test `run` function."""
    toml = Path(__file__).parent / "data/context.toml"
    ref_context_conf = Context.load(path=toml)

    ref_app_conf = AppConf(
        name="helloworld",
        python_application="app:app",
        healthcheck_endpoint="/",
        tests_cmd="pytest",
        tests_requirements=["intel-sgx-ra", "pytest==7.2.0"],
        cloud=CloudConf(
            project="default",
            hardware="free",
            code="/tmp/code",
            tests="/home/user/tests",
            docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
            ssl=SSLConf(
                domain_name="demo.dev.cosmilink.com",
                private_key=Path(__file__).parent / "data/key.pem",
                certificate=Path(__file__).parent / "data/cert.pem",
            ),
        ),
    )

    conf = Context.from_app_conf(conf=ref_app_conf)
    ref_context_conf.config.code_secret_key = conf.config.code_secret_key
    conf.run(
        app_id=UUID("d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e"),
        enclave_size=1,
        config_domain_name="demo.dev.cosmilink.com",
        expires_at=datetime.strptime(
            "2022-11-18T16:22:11.516125", "%Y-%m-%dT%H:%M:%S.%f"
        ),
        ssl_certificate_origin=SSLCertificateOrigin.Owner,
        nonces={"app.py": "f33f4a1a1555660f9396aea7811b0ff7b0f19503a7485914"},
    )

    ref_context_conf.workspace = conf.workspace

    assert conf == ref_context_conf


def test_save():
    """Test the `save` method."""
    toml = Path(__file__).parent / "data/context.toml"
    conf = Context.load(path=toml)
    os.makedirs(conf.workspace, exist_ok=True)
    code = conf.workspace / "app.tar"
    code.write_text("test")

    conf.save()

    assert filecmp.cmp(toml, conf.path)

    code_new = (
        conf.get_dirpath("d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e")
        / conf.get_tar_code_filename()
    )
    assert filecmp.cmp(code, code_new)


def test_path():
    """Test path handling methods."""
    toml = Path(__file__).parent / "data/context.toml"
    conf = Context.load(path=toml)
    workspace = conf.workspace

    assert conf.workspace.exists()
    assert conf.docker_log_path == workspace / "docker.log"
    assert conf.config_cert_path == workspace / "ratls.pem"
    assert conf.app_cert_path == workspace / "fullchain.pem"
    assert conf.decrypted_code_path == workspace / "decrypted_code"
    assert conf.decrypted_code_path.exists()
    assert conf.encrypted_code_path == workspace / "encrypted_code"
    assert conf.encrypted_code_path.exists()
    assert conf.tar_code_path == workspace / "app.tar"
    assert (
        conf.path
        == Path(
            "~/.config/mse/context/d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e/context.mse"
        ).expanduser()
    )
