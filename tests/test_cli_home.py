"""Test command/*.py."""
import base64
import io
import os
import re
import time
from argparse import Namespace
from pathlib import Path

import pytest
import requests
from conftest import capture_logs
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from mse_cli.home.command.code_provider.decrypt import run as do_decrypt
from mse_cli.home.command.code_provider.localtest import run as do_test_dev
from mse_cli.home.command.code_provider.package import run as do_package
from mse_cli.home.command.code_provider.scaffold import run as do_scaffold
from mse_cli.home.command.code_provider.seal import run as do_seal
from mse_cli.home.command.code_provider.verify import run as do_verify
from mse_cli.home.command.sgx_operator.evidence import run as do_evidence
from mse_cli.home.command.sgx_operator.list_all import run as do_list
from mse_cli.home.command.sgx_operator.logs import run as do_logs
from mse_cli.home.command.sgx_operator.restart import run as do_restart
from mse_cli.home.command.sgx_operator.run import run as do_run
from mse_cli.home.command.sgx_operator.spawn import run as do_spawn
from mse_cli.home.command.sgx_operator.status import run as do_status
from mse_cli.home.command.sgx_operator.stop import run as do_stop
from mse_cli.home.command.sgx_operator.test import run as do_test


@pytest.mark.home
@pytest.mark.incremental
def test_scaffold(workspace, app_name):
    """Test the `scaffold` subcommand."""
    # Go into a unique tmp directory
    os.chdir(workspace)

    # Run scaffold
    do_scaffold(Namespace(**{"app_name": app_name}))

    # Check creation of files
    path = workspace / app_name
    pytest.app_path = path

    assert path.exists()
    assert (path / "Dockerfile").exists()
    assert (path / "mse.toml").exists()
    assert (path / "secrets.json").exists()
    assert (path / "secrets_to_seal.json").exists()
    assert (path / "mse_src").exists()
    assert (path / "mse_src" / "app.py").exists()
    assert (path / "mse_src" / ".mseignore").exists()
    assert (path / "tests").exists()


@pytest.mark.home
@pytest.mark.incremental
def test_test_dev(cmd_log: io.StringIO):
    """Test the `test-dev` subcommand."""
    do_test_dev(
        Namespace(
            **{
                "project": None,
                "code": pytest.app_path / "mse_src",
                "dockerfile": pytest.app_path / "Dockerfile",
                "config": pytest.app_path / "mse.toml",
                "secrets": pytest.app_path / "secrets.json",
                "sealed_secrets": pytest.app_path / "secrets_to_seal.json",
                "test": pytest.app_path / "tests",
                "no_tests": False,
            }
        )
    )

    # Check the tar generation
    assert "Tests successful" in capture_logs(cmd_log)


@pytest.mark.home
@pytest.mark.incremental
def test_test_dev_project(cmd_log: io.StringIO):
    """Test the `test-dev` subcommand by specifying a project directory."""
    do_test_dev(
        Namespace(
            **{
                "project": pytest.app_path,
                "code": None,
                "dockerfile": None,
                "config": None,
                "secrets": None,
                "sealed_secrets": None,
                "test": None,
                "no_tests": False,
            }
        )
    )

    # Check the tar generation
    assert "Tests successful" in capture_logs(cmd_log)


@pytest.mark.home
@pytest.mark.incremental
def test_package(workspace: Path, cmd_log: io.StringIO):
    """Test the `package` subcommand."""
    do_package(
        Namespace(
            **{
                "project": None,
                "code": pytest.app_path / "mse_src",
                "config": pytest.app_path / "mse.toml",
                "dockerfile": pytest.app_path / "Dockerfile",
                "test": pytest.app_path / "tests",
                "encrypt": True,
                "output": workspace,
            }
        )
    )

    # Check the tar generation
    output = capture_logs(cmd_log)
    try:
        pytest.key_path = Path(
            re.search(
                "Your code secret key has been saved at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )

        pytest.package_path = Path(
            re.search(
                "Your package is now ready to be shared: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.package_path.exists()


@pytest.mark.home
@pytest.mark.incremental
def test_package_project(workspace: Path, cmd_log: io.StringIO):
    """Test the `package` subcommand by specifying a project directory."""
    do_package(
        Namespace(
            **{
                "project": pytest.app_path,
                "code": None,
                "config": None,
                "dockerfile": None,
                "test": None,
                "encrypt": True,
                "output": workspace,
            }
        )
    )

    # Check the tar generation
    output = capture_logs(cmd_log)
    try:
        pytest.key_path = Path(
            re.search(
                "Your code secret key has been saved at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )

        pytest.package_path = Path(
            re.search(
                "Your package is now ready to be shared: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.package_path.exists()


@pytest.mark.home
@pytest.mark.incremental
def test_spawn(
    workspace: Path,
    cmd_log: io.StringIO,
    app_name: str,
    port: int,
    host: str,
    signer_key: Path,
    pccs_url: str,
):
    """Test the `spawn` subcommand."""
    do_spawn(
        Namespace(
            **{
                "name": app_name,
                "pccs": pccs_url,
                "package": pytest.package_path,
                "host": host,
                "subject": f"CN={host},O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
                "san": host,
                "days": 2,
                "port": port,
                "size": 4096,
                "timeout": 5,
                "signer_key": signer_key,
                "output": workspace,
            }
        )
    )

    output = capture_logs(cmd_log)
    try:
        pytest.evidence_path = Path(
            re.search(
                "The evidence file has been generated at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.evidence_path.exists()


@pytest.mark.home
@pytest.mark.incremental
def test_logs(cmd_log: io.StringIO, app_name: str):
    """Test the `logs` subcommand."""
    do_logs(Namespace(**{"name": app_name, "follow": False}))

    output = capture_logs(cmd_log)
    try:
        pytest.fingerprint = re.search(
            "Measurement:\n[ ]*([a-z0-9]{64})", output
        ).group(1)
    except AttributeError:
        print(output)
        assert False

    assert "Starting the configuration server..." in output


@pytest.mark.home
@pytest.mark.incremental
def test_status_conf_server(cmd_log: io.StringIO, app_name: str, port: int, host: str):
    """Test the `status` subcommand on the conf server."""
    do_status(
        Namespace(
            **{
                "name": app_name,
            }
        )
    )

    output = capture_logs(cmd_log)

    assert f"App name = {app_name}" in output
    assert "Enclave size = 4096M" in output
    assert f"Common name = {host}" in output
    assert f"Port = {port}" in output
    assert "Healthcheck = /health" in output
    assert "Status = waiting secret keys" in output


@pytest.mark.home
@pytest.mark.incremental
def test_evidence(workspace: Path, cmd_log: io.StringIO, app_name: str, pccs_url: str):
    """Test the `evidence` subcommand."""
    do_evidence(
        Namespace(
            **{
                "name": app_name,
                "pccs": pccs_url,
                "output": workspace,
            }
        )
    )

    output = capture_logs(cmd_log)
    try:
        pytest.evidence_path = Path(
            re.search(
                "The evidence file has been generated at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.evidence_path.exists()


@pytest.mark.home
@pytest.mark.incremental
def test_verify(workspace: Path, cmd_log: io.StringIO):
    """Test the `verify` subcommand."""
    do_verify(
        Namespace(
            **{
                "package": pytest.package_path,
                "evidence": pytest.evidence_path,
                "output": workspace,
            }
        )
    )

    output = capture_logs(cmd_log)

    assert "Verification successful" in output

    try:
        pytest.ratls_cert = Path(
            re.search(
                "The RA-TLS certificate has been saved at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.ratls_cert.exists()


@pytest.mark.home
@pytest.mark.incremental
def test_seal(workspace: Path, cmd_log: io.StringIO):
    """Test the `seal` subcommand."""
    do_seal(
        Namespace(
            **{
                "secrets": pytest.app_path / "secrets_to_seal.json",
                "cert": pytest.ratls_cert,
                "output": workspace,
            }
        )
    )

    output = capture_logs(cmd_log)
    try:
        pytest.sealed_secrets = Path(
            re.search(
                "Your sealed secrets has been saved at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.sealed_secrets.exists()


@pytest.mark.home
@pytest.mark.incremental
def test_run(cmd_log: io.StringIO, app_name: str):
    """Test the `run` subcommand."""
    do_run(
        Namespace(
            **{
                "name": app_name,
                "key": pytest.key_path,
                "timeout": 5,
                "secrets": pytest.app_path / "secrets.json",
                "sealed_secrets": pytest.sealed_secrets,
            }
        )
    )

    assert "Application ready!" in capture_logs(cmd_log)


@pytest.mark.home
@pytest.mark.incremental
def test_test(
    app_name: str,
    cmd_log: io.StringIO,
):
    """Test the `test` subcommand."""
    do_test(
        Namespace(
            **{
                "name": app_name,
                "test": pytest.app_path / "tests",
                "config": pytest.app_path / "mse.toml",
            }
        )
    )

    assert "Tests successful" in capture_logs(cmd_log)


@pytest.mark.home
@pytest.mark.incremental
def test_decrypt_secrets_json(workspace: Path, port: int, host: str):
    """Test the `decrypt` subcommand with the secret json file."""
    response = requests.get(
        url=f"https://{host}:{port}/result/secrets",
        verify=pytest.ratls_cert,
        timeout=5,
    )

    assert response.status_code == 200

    enc_file_path = workspace / "result.enc"
    enc_file_path.write_bytes(response.content)

    key_path = workspace / "key.bin"
    salt: bytes = base64.urlsafe_b64decode(
        b"NICFe3qjykoE_DCSng22uzd6Pks3P2HHnaF-y9G18qo="
    )
    password: bytes = "qwerty".encode("utf-8")
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key_path.write_bytes(base64.urlsafe_b64encode(kdf.derive(password)))

    output_path = workspace / "result.plain"

    do_decrypt(
        Namespace(
            **{
                "key": key_path,
                "file": enc_file_path,
                "output": output_path,
            }
        )
    )

    assert output_path.exists()
    assert output_path.read_text() == "message using password and salt from SECRETS"


@pytest.mark.home
@pytest.mark.incremental
def test_decrypt_sealed_secrets_json(workspace: Path, port: int, host: str):
    """Test the `decrypt` subcommand with the sealed secret json file."""
    response = requests.get(
        url=f"https://{host}:{port}/result/sealed_secrets",
        verify=pytest.ratls_cert,
        timeout=5,
    )

    assert response.status_code == 200

    enc_file_path = workspace / "result2.enc"
    enc_file_path.write_bytes(response.content)

    key_path = workspace / "key2.bin"
    key_path.write_bytes(b"AXIKImqLJa5SZms7o6mb_nL1QLro_GDNcpIJQ71CgMk=")

    output_path = workspace / "result2.plain"

    do_decrypt(
        Namespace(
            **{
                "key": key_path,
                "file": enc_file_path,
                "output": output_path,
            }
        )
    )

    assert output_path.exists()
    assert output_path.read_text() == "message using result_sk from SEALED_SECRETS"


@pytest.mark.home
@pytest.mark.incremental
def test_status(cmd_log: io.StringIO, app_name: str, port: int, host: str):
    """Test the `status` subcommand."""
    do_status(
        Namespace(
            **{
                "name": app_name,
            }
        )
    )

    output = capture_logs(cmd_log)

    assert f"App name = {app_name}" in output
    assert "Enclave size = 4096M" in output
    assert f"Common name = {host}" in output
    assert f"Port = {port}" in output
    assert "Healthcheck = /health" in output
    assert "Status = running" in output


@pytest.mark.home
@pytest.mark.incremental
def test_list(cmd_log: io.StringIO, app_name: str):
    """Test the `list` subcommand."""
    do_list(Namespace())

    output = capture_logs(cmd_log)

    assert f"running   | {app_name}" in output


@pytest.mark.home
@pytest.mark.incremental
def test_stop(cmd_log: io.StringIO, app_name: str):
    """Test the `stop` subcommand."""
    do_stop(Namespace(**{"name": app_name, "remove": False}))

    output = capture_logs(cmd_log)

    assert f"Docker '{app_name}' has been stopped!" in output
    assert f"Docker '{app_name}' has been removed!" not in output

    do_status(
        Namespace(
            **{
                "name": app_name,
            }
        )
    )

    output = capture_logs(cmd_log)

    assert "Status = exited" in output

    do_list(Namespace())

    output = capture_logs(cmd_log)

    assert f"exited   | {app_name}" in output


@pytest.mark.home
@pytest.mark.incremental
def test_restart(cmd_log: io.StringIO, app_name: str):
    """Test the `restart` subcommand."""
    do_restart(Namespace(**{"name": app_name}))

    output = capture_logs(cmd_log)

    assert f"Docker '{app_name}' is now restarted!" in output

    time.sleep(10)

    do_status(
        Namespace(
            **{
                "name": app_name,
            }
        )
    )

    output = capture_logs(cmd_log)

    assert "Status = running" in output

    do_list(Namespace())

    output = capture_logs(cmd_log)

    assert f"running   | {app_name}" in output


@pytest.mark.home
@pytest.mark.incremental
def test_remove(cmd_log: io.StringIO, app_name: str):
    """Test the `stop` subcommand with removing."""
    do_stop(Namespace(**{"name": app_name, "remove": True}))

    output = capture_logs(cmd_log)

    assert f"Docker '{app_name}' has been stopped!" in output
    assert f"Docker '{app_name}' has been removed!" in output

    with pytest.raises(Exception):
        do_status(
            Namespace(
                **{
                    "name": app_name,
                }
            )
        )

    do_list(Namespace())

    output = capture_logs(cmd_log)

    assert f"{app_name}" not in output


@pytest.mark.home
@pytest.mark.incremental
def test_plaintext(
    workspace: Path,
    cmd_log: io.StringIO,
    app_name: str,
    port2: int,
    host: str,
    signer_key: Path,
    pccs_url: str,
):
    """Test the process subcommand without encryption."""
    do_package(
        Namespace(
            **{
                "project": None,
                "code": pytest.app_path / "mse_src",
                "config": pytest.app_path / "mse.toml",
                "dockerfile": pytest.app_path / "Dockerfile",
                "test": pytest.app_path / "tests",
                "encrypt": False,  # We do not encrypt here
                "output": workspace,
            }
        )
    )

    # Check the tar generation
    output = capture_logs(cmd_log)
    try:
        assert "Your code secret key has been saved at" not in output

        pytest.package_path = Path(
            re.search(
                "Your package is now ready to be shared: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.package_path.exists()

    do_spawn(
        Namespace(
            **{
                "name": app_name,
                "package": pytest.package_path,
                "host": host,
                "subject": f"CN={host},O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
                "san": host,
                "days": 2,
                # We use `port2` because we do not manage when
                # docker releases the free previous port
                "port": port2,
                "size": 4096,
                "timeout": 5,
                "signer_key": signer_key,
                "pccs": pccs_url,
                "output": workspace,
            }
        )
    )

    output = capture_logs(cmd_log)
    try:
        pytest.evidence_path = Path(
            re.search(
                "The evidence file has been generated at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.evidence_path.exists()

    do_run(
        Namespace(
            **{
                "name": app_name,
                "key": None,
                "timeout": 5,
                "secrets": None,
                "sealed_secrets": None,
            }
        )
    )

    assert "Application ready!" in capture_logs(cmd_log)

    do_test(
        Namespace(
            **{
                "name": app_name,
                "test": pytest.app_path / "tests",
                "config": pytest.app_path / "mse.toml",
            }
        )
    )

    assert "Tests successful" in capture_logs(cmd_log)

    do_stop(Namespace(**{"name": app_name, "remove": True}))

    output = capture_logs(cmd_log)

    assert f"Docker '{app_name}' has been stopped!" in output
    assert f"Docker '{app_name}' has been removed!" in output


@pytest.mark.home
@pytest.mark.incremental
def test_plaintext_project(
    workspace: Path,
    cmd_log: io.StringIO,
    app_name: str,
    port3: int,
    host: str,
    signer_key: Path,
    pccs_url: str,
):
    """Test the process subcommand without encryption by specifying a project directory."""
    do_package(
        Namespace(
            **{
                "project": pytest.app_path,
                "code": None,
                "config": None,
                "dockerfile": None,
                "test": None,
                "encrypt": False,  # We do not encrypt here
                "output": workspace,
            }
        )
    )

    # Check the tar generation
    output = capture_logs(cmd_log)
    try:
        assert "Your code secret key has been saved at" not in output

        pytest.package_path = Path(
            re.search(
                "Your package is now ready to be shared: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.package_path.exists()

    do_spawn(
        Namespace(
            **{
                "name": app_name,
                "pccs": pccs_url,
                "package": pytest.package_path,
                "host": host,
                "subject": f"CN={host},O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
                "san": host,
                "days": 2,
                # We use `port3` because we do not manage when
                # docker releases the free previous port
                "port": port3,
                "timeout": 5,
                "size": 4096,
                "signer_key": signer_key,
                "output": workspace,
            }
        )
    )

    output = capture_logs(cmd_log)
    try:
        pytest.evidence_path = Path(
            re.search(
                "The evidence file has been generated at: ([A-Za-z0-9/._-]+)", output
            ).group(1)
        )
    except AttributeError:
        print(output)
        assert False

    assert pytest.evidence_path.exists()

    do_run(
        Namespace(
            **{
                "name": app_name,
                "key": None,
                "timeout": 5,
                "secrets": None,
                "sealed_secrets": None,
            }
        )
    )

    assert "Application ready!" in capture_logs(cmd_log)

    do_test(
        Namespace(
            **{
                "name": app_name,
                "test": pytest.app_path / "tests",
                "config": pytest.app_path / "mse.toml",
            }
        )
    )

    assert "Tests successful" in capture_logs(cmd_log)

    do_stop(Namespace(**{"name": app_name, "remove": True}))

    output = capture_logs(cmd_log)

    assert f"Docker '{app_name}' has been stopped!" in output
    assert f"Docker '{app_name}' has been removed!" in output
