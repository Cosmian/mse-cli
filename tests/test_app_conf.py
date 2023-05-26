"""Test conf/app.py."""

import filecmp
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from mse_cli.model.app import AppConf, CodeConf, SSLConf

PRIVATE_KEY = "-----BEGIN PRIVATE"

CERTIFICATE = """-----BEGIN CERTIFICATE-----
MIIEYTCCA0mgAwIBAgISAwxw8+/Z9R9eGAFT3pJO/p4kMA0GCSqGSIb3DQEBCwUA
MDIxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQD
EwJSMzAeFw0yMzAzMzEwNzMzNTlaFw0yMzA2MjkwNzMzNThaMB4xHDAaBgNVBAMM
EyouZGV2LmNvc21pbGluay5jb20wWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATp
quvX2RGZpTvyAdKXYq2Xn6Im10LivhW5LJYHC0o+Vx6zh6fq7NghVuVwX+DD6bfu
3UweMNOaj6C7E4QSuRSVo4ICTjCCAkowDgYDVR0PAQH/BAQDAgeAMB0GA1UdJQQW
MBQGCCsGAQUFBwMBBggrBgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBSV
eq5hmkC6v7m+PhSWjazpzu1JJDAfBgNVHSMEGDAWgBQULrMXt1hWy65QCUDmH6+d
ixTCxjBVBggrBgEFBQcBAQRJMEcwIQYIKwYBBQUHMAGGFWh0dHA6Ly9yMy5vLmxl
bmNyLm9yZzAiBggrBgEFBQcwAoYWaHR0cDovL3IzLmkubGVuY3Iub3JnLzAeBgNV
HREEFzAVghMqLmRldi5jb3NtaWxpbmsuY29tMEwGA1UdIARFMEMwCAYGZ4EMAQIB
MDcGCysGAQQBgt8TAQEBMCgwJgYIKwYBBQUHAgEWGmh0dHA6Ly9jcHMubGV0c2Vu
Y3J5cHQub3JnMIIBBAYKKwYBBAHWeQIEAgSB9QSB8gDwAHYAtz77JN+cTbp18jnF
ulj0bF38Qs96nzXEnh0JgSXttJkAAAGHNs1YUQAABAMARzBFAiEAyA3P1CVW/owH
UeIshUd2markKt+lwNQBdi7GPnp5N98CIEI90wwjs2z6Kv7j50t+Jo6zHaJcdkpe
1Co84k1Kf593AHYArfe++nz/EMiLnT2cHj4YarRnKV3PsQwkyoWGNOvcgooAAAGH
Ns1YhgAABAMARzBFAiB5OrNt5zXxVq+d2UyJTnEXg4x8KP1Jnqi/uWqY1nMbJwIh
AKBP7wteQGLnIlrbjhwB33JvYskBqpXqOQKhdUnt5HyTMA0GCSqGSIb3DQEBCwUA
A4IBAQBWLHIBldUam/s9+YtKVrOHIPbIg6WmztASPtnH1q2ehzTuxJw9R3qMiGAo
S2LHEYBPtjWfBJMB53SD39Mlvj8KDLRlRtFNv0j5OrddKEp8TJZjsEnncpRJYLH4
USyBj48HeYukzYuW34e7GhcqbR5Y4foKah9hMY0mNYS8CQ9gvhGDQXZjtb0NT0OC
3uQFNovYfowmh3AugCGMHPfHJBdCYp3OWP06kMUIF0HcUf14LN59mTjLbWvpMFZY
hTzDLxa9dujgnpDt4cWU7ImCdxPLYerbg5LMgW3vXD1QKQIFDeZLwXKw2Nb5o3MU
E9X9WRkFtRDUHOj0PxL20reOi3jJ
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFFjCCAv6gAwIBAgIRAJErCErPDBinU/bWLiWnX1owDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMjAwOTA0MDAwMDAw
WhcNMjUwOTE1MTYwMDAwWjAyMQswCQYDVQQGEwJVUzEWMBQGA1UEChMNTGV0J3Mg
RW5jcnlwdDELMAkGA1UEAxMCUjMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
AoIBAQC7AhUozPaglNMPEuyNVZLD+ILxmaZ6QoinXSaqtSu5xUyxr45r+XXIo9cP
R5QUVTVXjJ6oojkZ9YI8QqlObvU7wy7bjcCwXPNZOOftz2nwWgsbvsCUJCWH+jdx
sxPnHKzhm+/b5DtFUkWWqcFTzjTIUu61ru2P3mBw4qVUq7ZtDpelQDRrK9O8Zutm
NHz6a4uPVymZ+DAXXbpyb/uBxa3Shlg9F8fnCbvxK/eG3MHacV3URuPMrSXBiLxg
Z3Vms/EY96Jc5lP/Ooi2R6X/ExjqmAl3P51T+c8B5fWmcBcUr2Ok/5mzk53cU6cG
/kiFHaFpriV1uxPMUgP17VGhi9sVAgMBAAGjggEIMIIBBDAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0lBBYwFAYIKwYBBQUHAwIGCCsGAQUFBwMBMBIGA1UdEwEB/wQIMAYB
Af8CAQAwHQYDVR0OBBYEFBQusxe3WFbLrlAJQOYfr52LFMLGMB8GA1UdIwQYMBaA
FHm0WeZ7tuXkAXOACIjIGlj26ZtuMDIGCCsGAQUFBwEBBCYwJDAiBggrBgEFBQcw
AoYWaHR0cDovL3gxLmkubGVuY3Iub3JnLzAnBgNVHR8EIDAeMBygGqAYhhZodHRw
Oi8veDEuYy5sZW5jci5vcmcvMCIGA1UdIAQbMBkwCAYGZ4EMAQIBMA0GCysGAQQB
gt8TAQEBMA0GCSqGSIb3DQEBCwUAA4ICAQCFyk5HPqP3hUSFvNVneLKYY611TR6W
PTNlclQtgaDqw+34IL9fzLdwALduO/ZelN7kIJ+m74uyA+eitRY8kc607TkC53wl
ikfmZW4/RvTZ8M6UK+5UzhK8jCdLuMGYL6KvzXGRSgi3yLgjewQtCPkIVz6D2QQz
CkcheAmCJ8MqyJu5zlzyZMjAvnnAT45tRAxekrsu94sQ4egdRCnbWSDtY7kh+BIm
lJNXoB1lBMEKIq4QDUOXoRgffuDghje1WrG9ML+Hbisq/yFOGwXD9RiX8F6sw6W4
avAuvDszue5L3sz85K+EC4Y/wFVDNvZo4TYXao6Z0f+lQKc0t8DQYzk1OXVu8rp2
yJMC6alLbBfODALZvYH7n7do1AZls4I9d1P4jnkDrQoxB3UqQ9hVl3LEKQ73xF1O
yK5GhDDX8oVfGKF5u+decIsH4YaTw7mP3GFxJSqv3+0lUFJoi5Lc5da149p90Ids
hCExroL1+7mryIkXPeFM5TgO9r0rvZaBFOvV2z0gp35Z0+L4WPlbuEjN/lxPFin+
HlUjr8gRsI3qfJOQFy/9rKIJR0Y/8Omwt/8oTWgy1mdeHmmjk7j1nYsvC9JSQ6Zv
MldlTTKB3zhThV1+XWYp6rjd5JW1zbVWEkLNxE7GJThEUG3szgBVGP7pSWTUTsqX
nLRbwHOoq7hHwg==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFYDCCBEigAwIBAgIQQAF3ITfU6UK47naqPGQKtzANBgkqhkiG9w0BAQsFADA/
MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT
DkRTVCBSb290IENBIFgzMB4XDTIxMDEyMDE5MTQwM1oXDTI0MDkzMDE4MTQwM1ow
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwggIiMA0GCSqGSIb3DQEB
AQUAA4ICDwAwggIKAoICAQCt6CRz9BQ385ueK1coHIe+3LffOJCMbjzmV6B493XC
ov71am72AE8o295ohmxEk7axY/0UEmu/H9LqMZshftEzPLpI9d1537O4/xLxIZpL
wYqGcWlKZmZsj348cL+tKSIG8+TA5oCu4kuPt5l+lAOf00eXfJlII1PoOK5PCm+D
LtFJV4yAdLbaL9A4jXsDcCEbdfIwPPqPrt3aY6vrFk/CjhFLfs8L6P+1dy70sntK
4EwSJQxwjQMpoOFTJOwT2e4ZvxCzSow/iaNhUd6shweU9GNx7C7ib1uYgeGJXDR5
bHbvO5BieebbpJovJsXQEOEO3tkQjhb7t/eo98flAgeYjzYIlefiN5YNNnWe+w5y
sR2bvAP5SQXYgd0FtCrWQemsAXaVCg/Y39W9Eh81LygXbNKYwagJZHduRze6zqxZ
Xmidf3LWicUGQSk+WT7dJvUkyRGnWqNMQB9GoZm1pzpRboY7nn1ypxIFeFntPlF4
FQsDj43QLwWyPntKHEtzBRL8xurgUBN8Q5N0s8p0544fAQjQMNRbcTa0B7rBMDBc
SLeCO5imfWCKoqMpgsy6vYMEG6KDA0Gh1gXxG8K28Kh8hjtGqEgqiNx2mna/H2ql
PRmP6zjzZN7IKw0KKP/32+IVQtQi0Cdd4Xn+GOdwiK1O5tmLOsbdJ1Fu/7xk9TND
TwIDAQABo4IBRjCCAUIwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMCAQYw
SwYIKwYBBQUHAQEEPzA9MDsGCCsGAQUFBzAChi9odHRwOi8vYXBwcy5pZGVudHJ1
c3QuY29tL3Jvb3RzL2RzdHJvb3RjYXgzLnA3YzAfBgNVHSMEGDAWgBTEp7Gkeyxx
+tvhS5B1/8QVYIWJEDBUBgNVHSAETTBLMAgGBmeBDAECATA/BgsrBgEEAYLfEwEB
ATAwMC4GCCsGAQUFBwIBFiJodHRwOi8vY3BzLnJvb3QteDEubGV0c2VuY3J5cHQu
b3JnMDwGA1UdHwQ1MDMwMaAvoC2GK2h0dHA6Ly9jcmwuaWRlbnRydXN0LmNvbS9E
U1RST09UQ0FYM0NSTC5jcmwwHQYDVR0OBBYEFHm0WeZ7tuXkAXOACIjIGlj26Ztu
MA0GCSqGSIb3DQEBCwUAA4IBAQAKcwBslm7/DlLQrt2M51oGrS+o44+/yQoDFVDC
5WxCu2+b9LRPwkSICHXM6webFGJueN7sJ7o5XPWioW5WlHAQU7G75K/QosMrAdSW
9MUgNTP52GE24HGNtLi1qoJFlcDyqSMo59ahy2cI2qBDLKobkx/J3vWraV0T9VuG
WCLKTVXkcGdtwlfFRjlBz4pYg1htmf5X6DYO8A4jqv2Il9DjXA6USbW1FzXSLr9O
he8Y4IWS6wY7bCkjCWDcRQJMEhg76fsO3txE+FiYruq9RUWhiF1myv4Q6W+CyBFC
Dfvp7OOGAN6dEOM4+qR9sdjoSYKEBpsr6GtPAQw4dy753ec5
-----END CERTIFICATE-----"""


def test_ssl():
    """Test `ssl` paragraph."""
    toml = Path("tests/data/ssl.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(
        location="/tmp/code",
        python_application="app:app",
        healthcheck_endpoint="/",
        docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
    )

    ssl = SSLConf(
        domain_name="demo.dev.cosmilink.com",
        private_key=Path(__file__).parent / "data" / Path("key.pem"),
        certificate=Path(__file__).parent / "data" / Path("cert.pem"),
    )

    ref_app_conf = AppConf(
        name="helloworld",
        project="default",
        hardware="4g-eu-001",
        expiration_date=datetime(2023, 6, 29, 0, 0, 0, tzinfo=timezone.utc),
        code=code,
        ssl=ssl,
    )

    assert conf == ref_app_conf
    assert conf.ssl.certificate_data == CERTIFICATE
    assert conf.ssl.private_key_data == PRIVATE_KEY


def test_ssl_optionals():
    """Test conf with optionals as None."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(
        location="/tmp/code",
        python_application="app:ppa",
        healthcheck_endpoint="/",
        docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
    )

    ref_app_conf = AppConf(
        name="helloworld",
        project="default",
        hardware="4g-eu-001",
        code=code,
        ssl=None,
    )

    assert conf == ref_app_conf


def test_ignore_ssl():
    """Test `ssl` paragraph."""
    toml = Path("tests/data/ssl.toml")
    conf = AppConf.from_toml(path=toml, ignore_ssl=True)

    code = CodeConf(
        location="/tmp/code",
        python_application="app:app",
        healthcheck_endpoint="/",
        docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
    )

    assert conf.ssl is None


def test_ssl_optionals():
    """Test conf with optionals as None."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(
        location="/tmp/code",
        python_application="app:ppa",
        healthcheck_endpoint="/",
        docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
        secrets=Path(__file__).parent / "data" / Path("secrets.json"),
    )

    ref_app_conf = AppConf(
        name="helloworld",
        version="1.0.0",
        project="default",
        hardware="4g-eu-001",
        code=code,
        ssl=None,
    )

    assert conf == ref_app_conf
    assert conf.code.secrets_data == {"login": "user", "password": "azerty"}


def test_expiration_date():
    """Test conf with `expiration_date` set."""
    toml = Path("tests/data/expiration_date.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(
        location="/tmp/code",
        python_application="app:app",
        healthcheck_endpoint="/",
        docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
    )

    ref_app_conf = AppConf(
        name="helloworld",
        project="default",
        hardware="4g-eu-001",
        code=code,
        expiration_date=datetime(2023, 6, 29, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert conf == ref_app_conf

    toml = Path("tests/data/optional_fields_ssl.toml")
    conf = AppConf.from_toml(path=toml)
    assert conf.expiration_date == datetime(2023, 6, 29, 7, 33, 58, tzinfo=timezone.utc)


def test_bad_domain_name():
    """Test error when domain name is not the same than in the cert."""
    toml = Path("tests/data/ssl_bad_domain_name.toml")
    with pytest.raises(Exception) as context:
        conf = AppConf.from_toml(path=toml)


def test_bad_expiration_date():
    """Test error when exp doesn't fit the one in the cert."""
    toml = Path("tests/data/ssl_bad_expiration_date.toml")
    with pytest.raises(Exception) as context:
        conf = AppConf.from_toml(path=toml)


def test_python_variable():
    """Test properties for `python_application` field."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    assert conf.python_module == "app"
    assert conf.python_variable == "ppa"

    code = CodeConf(
        location="/tmp/code",
        python_application="bad",
        healthcheck_endpoint="/",
        docker="ghcr.io/cosmian/mse-pytorch:20230104085621",
    )

    conf = AppConf(
        name="helloworld", project="default", hardware="4g-eu-001", code=code
    )

    with pytest.raises(Exception) as context:
        conf.python_variable
        conf.python_module


def test_app_identifier():
    """Test property `app_identifier`."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    assert conf.app_identifier == "helloworld"


def test_save():
    """Test `save` method."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)
    conf.code.secrets = "secrets.json"

    saved_path = Path(tempfile.gettempdir())
    conf.save(saved_path)

    assert filecmp.cmp(toml, saved_path / "mse.toml")

    toml = Path("tests/data/expiration_date.toml")
    conf = AppConf.from_toml(path=toml)

    saved_path = Path(tempfile.gettempdir())
    conf.save(saved_path)

    assert filecmp.cmp(toml, saved_path / "mse.toml")

    toml = Path("tests/data/ssl.toml")
    conf = AppConf.from_toml(path=toml)
    conf.ssl.private_key = "key.pem"
    conf.ssl.certificate = "cert.pem"

    saved_path = Path(tempfile.gettempdir())
    conf.save(saved_path)

    assert filecmp.cmp(toml, saved_path / "mse.toml")


def test_into_payload():
    """Test `into_payload` function."""
    toml = Path("tests/data/ssl.toml")
    conf = AppConf.from_toml(path=toml)
    assert conf.into_payload() == {
        "name": "helloworld",
        "project": "default",
        "healthcheck_endpoint": "/",
        "python_application": "app:app",
        "docker": "ghcr.io/cosmian/mse-pytorch:20230104085621",
        "expires_at": "2023-06-29T00:00:00.000000Z",
        "dev_mode": False,
        "ssl_certificate": CERTIFICATE,
        "domain_name": "demo.dev.cosmilink.com",
        "hardware": "4g-eu-001",
    }
