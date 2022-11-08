from pathlib import Path
import tempfile

from mse_ctl.conf.app import AppConf, SSLConf, CodeConf
import pytest
import filecmp


def test_ssl():
    """Test `ssl` paragraph."""
    toml = Path("tests/data/ssl.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(location="./code",
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

    assert conf == ref_app_conf


def test_optionals():
    """Test conf with optionals as None."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(location="./code",
                    encrypted=True,
                    python_application="app:ppa",
                    health_check_endpoint="/")

    ref_app_conf = AppConf(name="helloworld",
                           version="1.0.0",
                           project="default",
                           plan="free",
                           code=code,
                           ssl=None)

    assert conf == ref_app_conf


def test_shutdown_delay():
    """Test conf with `shutdown_delay` set."""
    toml = Path("tests/data/shutdown_delay.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(location="./code",
                    encrypted=True,
                    python_application="app:app",
                    health_check_endpoint="/")

    ref_app_conf = AppConf(name="helloworld",
                           version="1.0.0",
                           project="default",
                           plan="free",
                           code=code,
                           shutdown_delay=10)

    assert conf == ref_app_conf


def test_python_variable():
    """Test properties for `python_application` field."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    assert conf.python_module == "app"
    assert conf.python_variable == "ppa"

    code = CodeConf(location="./code",
                    encrypted=True,
                    python_application="bad",
                    health_check_endpoint="/")

    conf = AppConf(name="helloworld",
                   version="1.0.0",
                   project="default",
                   plan="free",
                   code=code,
                   shutdown_delay=10)

    with pytest.raises(Exception) as context:
        conf.python_variable
        conf.python_module


def test_service_identifier():
    """Test property `service_identifier`."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    assert conf.service_identifier == "helloworld-1.0.0"


def test_save():
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    saved_path = Path(tempfile.gettempdir())
    conf.save(saved_path)

    assert filecmp.cmp(toml, saved_path / "mse.toml")

    toml = Path("tests/data/shutdown_delay.toml")
    conf = AppConf.from_toml(path=toml)

    saved_path = Path(tempfile.gettempdir())
    conf.save(saved_path)

    assert filecmp.cmp(toml, saved_path / "mse.toml")

    toml = Path("tests/data/ssl.toml")
    conf = AppConf.from_toml(path=toml)

    saved_path = Path(tempfile.gettempdir())
    conf.save(saved_path)

    assert filecmp.cmp(toml, saved_path / "mse.toml")


def test_default():
    """Test `default` function."""
    conf = AppConf.default("helloworld", Path("."))

    code = CodeConf(location="./code",
                    encrypted=True,
                    python_application="app:app",
                    health_check_endpoint="/")

    app_ref = AppConf(name="helloworld",
                      version="0.1.0",
                      project="default",
                      plan="free",
                      code=code)

    assert app_ref == conf


def test_into_payload():
    """Test `into_payload` function."""
    toml = Path("tests/data/ssl.toml")
    conf = AppConf.from_toml(path=toml)
    assert conf.into_payload() == {
        "name": "helloworld",
        "version": "1.0.0",
        "project": "default",
        "encrypted_code": True,
        "health_check_endpoint": "/",
        "python_application": "app:app",
        "shutdown_delay": None,
        "ssl_certificate": "-----BEGIN CERTIFICATE",
        "domain_name": "demo.cosmian.app",
        "plan": "free",
    }