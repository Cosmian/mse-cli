import filecmp
from pathlib import Path
from uuid import UUID
from mse_ctl.conf.app import AppConf, CodeConf, SSLConf

from mse_ctl.conf.context import AppCertificateOrigin, Context


def test_from_toml():
    """Test `from_toml` function."""
    toml = Path("tests/data/context.toml")
    conf = Context.from_toml(path=toml)

    ref_context_conf = Context(
        name="helloworld",
        version="1.0.0",
        project="default",
        id="d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e",
        domain_name="demo.cosmian.app",
        symkey=
        "a389f8baf2e03cebd445d99f03600b29ca259faa9a3964e529c03effef206135",
        encrypted_code=True,
        enclave_size="1",
        expires_in=1,
        python_application="app:app",
        docker_version="11d789bf",
        app_certificate_origin=AppCertificateOrigin.Owner,
        ssl_app_certificate="-----BEGIN CERTIFICATE")

    assert conf == ref_context_conf


def test_from_app_conf():
    """Test `from_app_conf` function."""
    toml = Path("tests/data/context.toml")

    code = CodeConf(location="/tmp/code",
                    encrypted=True,
                    python_application="app:app",
                    health_check_endpoint="/")

    ssl = SSLConf(domain_name="demo.cosmian.app",
                  private_key="-----BEGIN PRIVATE",
                  certificate="-----BEGIN CERTIFICATE")

    ref_app_conf = AppConf(name="helloworld",
                           version="1.0.0",
                           project="default",
                           plan="free",
                           code=code,
                           ssl=ssl)

    conf = Context.from_app_conf(conf=ref_app_conf, enclave_size=1)

    ref_context_conf = Context(
        name="helloworld",
        version="1.0.0",
        project="default",
        id="00000000-0000-0000-0000-000000000000",
        domain_name="",
        symkey=conf.symkey,
        encrypted_code=True,
        enclave_size="1",
        expires_in=0,
        python_application="app:app",
        docker_version="",
        app_certificate_origin=AppCertificateOrigin.Owner,
        ssl_app_certificate="")

    assert conf == ref_context_conf


def test_run():
    """Test `from_app_conf` function."""
    toml = Path("tests/data/context.toml")
    ref_context_conf = Context.from_toml(path=toml)

    code = CodeConf(location="/tmp/code",
                    encrypted=True,
                    python_application="app:app",
                    health_check_endpoint="/")

    ssl = SSLConf(domain_name="demo.cosmian.app",
                  private_key="-----BEGIN PRIVATE",
                  certificate="-----BEGIN CERTIFICATE")

    ref_app_conf = AppConf(name="helloworld",
                           version="1.0.0",
                           project="default",
                           plan="free",
                           code=code,
                           ssl=ssl)

    conf = Context.from_app_conf(conf=ref_app_conf, enclave_size=1)
    ref_context_conf.symkey = conf.symkey
    conf.run(uuid=UUID("d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e"),
             domain_name="demo.cosmian.app",
             docker_version="11d789bf",
             expires_in=1,
             config_cert="-----BEGIN CERTIFICATE1",
             app_cert="-----BEGIN CERTIFICATE")

    assert conf == ref_context_conf
    assert conf.config_cert_path.read_text() == "-----BEGIN CERTIFICATE1"
    assert conf.app_cert_path.read_text() == "-----BEGIN CERTIFICATE"


def test_save():
    """Test the `save` method."""
    toml = Path("tests/data/context.toml")
    conf = Context.from_toml(path=toml)

    conf.save()

    assert filecmp.cmp(toml, conf.exported_path)


def test_path():
    """Test path handling methods."""
    toml = Path("tests/data/context.toml")
    conf = Context.from_toml(path=toml)

    assert conf.workspace == Path("/tmp/helloworld-1.0.0")
    assert conf.workspace.exists()
    assert conf.docker_log_path == Path("/tmp/helloworld-1.0.0/docker.log")
    assert conf.config_cert_path == Path("/tmp/helloworld-1.0.0/cert.conf.pem")
    assert conf.app_cert_path == Path("/tmp/helloworld-1.0.0/cert.app.pem")
    assert conf.decrypted_code_path == Path(
        "/tmp/helloworld-1.0.0/decrypted_code")
    assert conf.decrypted_code_path.exists()
    assert conf.encrypted_code_path == Path(
        "/tmp/helloworld-1.0.0/encrypted_code")
    assert conf.encrypted_code_path.exists()
    assert conf.tar_code_path == Path("/tmp/helloworld-1.0.0/code.tar")
    assert conf.exported_path == Path(
        "~/.config/mse-ctl/context/d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e.mse"
    ).expanduser()
