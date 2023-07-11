"""Test api/types.py."""

from datetime import datetime

from mse_cli.cloud.api.types import App, AppStatus, SSLCertificateOrigin


def test_is_terminated():
    """Test `is_terminated`."""

    app = App.from_dict(
        {
            "id": "00000000-0000-0000-0000-000000000000",
            "name": "a",
            "version": "b",
            "project_id": "00000000-0000-0000-0000-000000000000",
            "owner_id": "00000000-0000-0000-0000-000000000000",
            "domain_name": "a",
            "config_domain_name": "b",
            "docker": "c",
            "created_at": datetime.now(),
            "status": AppStatus.Spawning,
            "hardware_name": "4g-eu-001",
            "ssl_certificate_origin": SSLCertificateOrigin.Operator,
            "expires_at": datetime.now(),
            "python_application": "str",
            "healthcheck_endpoint": "str",
        }
    )
    assert not app.is_terminated()

    app.status = AppStatus.Initializing
    assert not app.is_terminated()

    app.status = AppStatus.Running
    assert not app.is_terminated()

    app.status = AppStatus.OnError
    assert app.is_terminated()

    app.status = AppStatus.Stopped
    assert app.is_terminated()
