"""Test conf/app.py."""

from pathlib import Path
from datetime import datetime, timezone
import tempfile

from mse_cli.conf.app import AppConf, SSLConf, CodeConf
import pytest
import filecmp

CERTIFICATE = """-----BEGIN CERTIFICATE-----
MIIFJjCCBA6gAwIBAgISBDPkIKr25kXNCnr4RF5abjE4MA0GCSqGSIb3DQEBCwUA
MDIxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQD
EwJSMzAeFw0yMjExMDgwODU0NTlaFw0yMzAyMDYwODU0NThaMBsxGTAXBgNVBAMT
EGRlbW8uY29zbWlhbi5hcHAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB
AQDEAsVKlImmxXFbMBvcftcv7adiKKZWZIOkjL9Vb2wLY/B4lXVVEMzVD1+gbvOb
FCaJqtdMonerKrlnd5IanC0LxFs4bdZwY51SMaM9gUW1SjNbsWT+ZZV8WP0REtQY
FNT3Ba9gOi7bKp/uSp2Ki73lM3XL0Tid3RH0u2Xg3Ai5ljHA99ka6hr/Nj+h4x0E
iQoguEN7j5pjt6WlazNxUP/bCeVSZ1to7bKVYDlq7FJmo+Q/NlpM4acQPd17Zoh+
9YofwCGLCRXoWNVCiNyTWyorQhCfJyBhz7Gixw3l+78EKw7c/ma2VLfn0+0nQzL7
yuxnqKVsheL9DoQfm7O7xjDhAgMBAAGjggJLMIICRzAOBgNVHQ8BAf8EBAMCBaAw
HQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMAwGA1UdEwEB/wQCMAAwHQYD
VR0OBBYEFKoekS8rZIbMzUumfrBDWk5dzAp/MB8GA1UdIwQYMBaAFBQusxe3WFbL
rlAJQOYfr52LFMLGMFUGCCsGAQUFBwEBBEkwRzAhBggrBgEFBQcwAYYVaHR0cDov
L3IzLm8ubGVuY3Iub3JnMCIGCCsGAQUFBzAChhZodHRwOi8vcjMuaS5sZW5jci5v
cmcvMBsGA1UdEQQUMBKCEGRlbW8uY29zbWlhbi5hcHAwTAYDVR0gBEUwQzAIBgZn
gQwBAgEwNwYLKwYBBAGC3xMBAQEwKDAmBggrBgEFBQcCARYaaHR0cDovL2Nwcy5s
ZXRzZW5jcnlwdC5vcmcwggEEBgorBgEEAdZ5AgQCBIH1BIHyAPAAdgC3Pvsk35xN
unXyOcW6WPRsXfxCz3qfNcSeHQmBJe20mQAAAYRWqh2yAAAEAwBHMEUCIAOi6Y7K
fBL17v3q02Bik1EkxQungIfEluFjacB0d9/rAiEAmk6fJr0EN3T4eFOhGL3y4v1B
cAMCPaalm1cLcsAR+L0AdgBvU3asMfAxGdiZAKRRFf93FRwR2QLBACkGjbIImjfZ
EwAAAYRWqh78AAAEAwBHMEUCIQD4w3nmWKWPgd1U9vIUPQlWsqjeYWfUwSdbK5+q
NKfzcgIgUzLXBtcM8jAXt/jTOSRiF7WNeGB2VbtB0MCazl4EneEwDQYJKoZIhvcN
AQELBQADggEBACe41Gxbr//luqD0lyCJh9vcNz8F6nd9SAJrJ/ERBpAHlTx7PXU6
r8XQ4Grv+FYNUjb0e8Hpp6EL3ejkJgwC0wIqO7d0Nq9wgaSEKuhKeFoinezPxEu6
ygmOIOC9fkkPYz+n+y/eydphayg45rth2uohcN4h+vWXT/gzUFNNMriettQ4VD/d
w9X89xLDuku40UFhyrq4El25X3Cz3QPsr+HQvqp/MU3eY44992Pqa/kBWOpiKnd3
K2veHwKvzfaZsjHUCerLary6FT341O+niEmAZ0SyzuC5FAtE6een6EPCMbxJfO9D
4AYwZ7MyI/swo0hPBVrykTSEwJDvToYHZn8=
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

    code = CodeConf(location="/tmp/code",
                    python_application="app:app",
                    health_check_endpoint="/",
                    docker="ghcr.io/cosmian/mse-pytorch:20230104085621")

    ssl = SSLConf(domain_name="demo.cosmian.app",
                  private_key="-----BEGIN PRIVATE",
                  certificate=CERTIFICATE)

    ref_app_conf = AppConf(name="helloworld",
                           version="1.0.0",
                           project="default",
                           plan="free",
                           expiration_date=datetime(2023,
                                                    2,
                                                    1,
                                                    0,
                                                    0,
                                                    0,
                                                    tzinfo=timezone.utc),
                           code=code,
                           ssl=ssl)

    assert conf == ref_app_conf


def test_ssl_optionals():
    """Test conf with optionals as None."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(location="/tmp/code",
                    python_application="app:ppa",
                    health_check_endpoint="/",
                    docker="ghcr.io/cosmian/mse-pytorch:20230104085621")

    ref_app_conf = AppConf(name="helloworld",
                           version="1.0.0",
                           project="default",
                           plan="free",
                           code=code,
                           ssl=None)

    assert conf == ref_app_conf


def test_expiration_date():
    """Test conf with `expiration_date` set."""
    toml = Path("tests/data/expiration_date.toml")
    conf = AppConf.from_toml(path=toml)

    code = CodeConf(location="/tmp/code",
                    python_application="app:app",
                    health_check_endpoint="/",
                    docker="ghcr.io/cosmian/mse-pytorch:20230104085621")

    ref_app_conf = AppConf(
        name="helloworld",
        version="1.0.0",
        project="default",
        plan="free",
        code=code,
        expiration_date=datetime(2023, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
    )

    assert conf == ref_app_conf

    toml = Path("tests/data/optional_fields_ssl.toml")
    conf = AppConf.from_toml(path=toml)
    assert conf.expiration_date == datetime(2023,
                                            2,
                                            6,
                                            8,
                                            54,
                                            58,
                                            tzinfo=timezone.utc)


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

    code = CodeConf(location="/tmp/code",
                    python_application="bad",
                    health_check_endpoint="/",
                    docker="ghcr.io/cosmian/mse-pytorch:20230104085621")

    conf = AppConf(name="helloworld",
                   version="1.0.0",
                   project="default",
                   plan="free",
                   code=code)

    with pytest.raises(Exception) as context:
        conf.python_variable
        conf.python_module


def test_service_identifier():
    """Test property `service_identifier`."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

    assert conf.service_identifier == "helloworld-1.0.0"


def test_save():
    """Test `save` method."""
    toml = Path("tests/data/optional_fields.toml")
    conf = AppConf.from_toml(path=toml)

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

    saved_path = Path(tempfile.gettempdir())
    conf.save(saved_path)

    assert filecmp.cmp(toml, saved_path / "mse.toml")


def test_default():
    """Test `default` function."""
    conf = AppConf.default("helloworld")

    code = CodeConf(location=Path("mse_code"),
                    python_application="app:app",
                    health_check_endpoint="/",
                    docker="ghcr.io/cosmian/mse-pytorch:20230104085621")

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
        "health_check_endpoint": "/",
        "python_application": "app:app",
        "docker": "ghcr.io/cosmian/mse-pytorch:20230104085621",
        "expires_at": '2023-02-01T00:00:00.000000Z',
        "dev_mode": False,
        "ssl_certificate": CERTIFICATE,
        "domain_name": "demo.cosmian.app",
        "plan": "free",
    }
