"""Test api/types.py."""

from datetime import datetime

from mse_cli.api.types import App, AppStatus, SSLCertificateOrigin


def test_is_terminated():
    """Test `is_terminated`."""

    app = App.from_dict({
        "uuid": "00000000-0000-0000-0000-000000000000",
        "name": "a",
        "version": "b",
        "project_uuid": "00000000-0000-0000-0000-000000000000",
        "owner_uuid": "00000000-0000-0000-0000-000000000000",
        "domain_name": "a",
        "config_domain_name": "b",
        "docker": "c",
        "created_at": datetime.now(),
        "status": AppStatus.Spawning,
        "plan": "free",
        "ssl_certificate_origin": SSLCertificateOrigin.Operator,
        "expires_at": datetime.now(),
        "python_application": "str",
        "healthcheck_endpoint": "str",
    })
    assert not app.is_terminated()

    app.status = AppStatus.Initializing
    assert not app.is_terminated()

    app.status = AppStatus.Running
    assert not app.is_terminated()

    app.status = AppStatus.OnError
    assert app.is_terminated()

    app.status = AppStatus.Stopped
    assert app.is_terminated()
