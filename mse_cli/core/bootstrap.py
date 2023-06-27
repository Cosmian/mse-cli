"""mse_cli.core.bootstrap module."""

from typing import Any, Callable, Dict, Iterable, Optional, Union
from uuid import UUID

import requests
from pydantic import BaseModel

from mse_cli.core.base64 import base64url_encode
from mse_cli.core.clock_tick import ClockTick
from mse_cli.error import UnexpectedResponse


class ConfigurationPayload(BaseModel):
    """Definition of the bootstrap server payload."""

    app_id: UUID
    secrets: Optional[Any]
    sealed_secrets: Optional[bytes]
    code_secret_key: Optional[bytes]
    ssl_private_key: Optional[str]

    def payload(self) -> Dict[str, Any]:
        """Build the payload to send to the configuration server."""
        data: Dict[str, Any] = {
            "uuid": str(self.app_id),
        }

        if self.secrets:
            data["app_secrets"] = self.secrets

        if self.sealed_secrets:
            data["app_sealed_secrets"] = base64url_encode(self.sealed_secrets)

        if self.code_secret_key:
            data["code_secret_key"] = self.code_secret_key.hex()

        if self.ssl_private_key:
            data["ssl_private_key"] = self.ssl_private_key

        return data


def configure_app(url: str, data: Dict[str, Any], verify: Union[bool, str] = True):
    """Send the secrets to the configuration server."""
    r = requests.post(
        url=url,
        json=data,
        headers={"Content-Type": "application/json"},
        verify=verify,
        timeout=60,
    )

    if not r.ok:
        raise UnexpectedResponse(
            "Fail to send data to the configuration server "
            f"(Response {r.status_code} {r.text})"
        )


def wait_for_conf_server(
    clock: ClockTick,
    url: str,
    verify: Union[bool, str] = True,
    extra_check: Optional[Callable] = None,
    extra_check_args: Iterable = (),
):
    """Hold on until the configuration server is up and listing."""
    while clock.tick():
        if extra_check:
            extra_check(*extra_check_args)

        if is_waiting_for_secrets(url, verify):
            break


def is_waiting_for_secrets(url: str, verify: Union[bool, str] = True) -> bool:
    """Check whether the configuration server is up."""
    try:
        response = requests.get(url=url, verify=verify, timeout=5)

        if response.status_code == 200 and "Mse-Status" in response.headers:
            return True
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.SSLError:
        return False
    except requests.exceptions.ConnectionError:
        return False

    return False


def wait_for_app_server(
    clock: ClockTick,
    url: str,
    healthcheck_endpoint: str,
    verify: Union[bool, str] = True,
    extra_check: Optional[Callable] = None,
    extra_check_args: Iterable = (),
):
    """Hold on until the configuration server is stopped and the app starts."""
    while clock.tick():
        if extra_check:
            extra_check(*extra_check_args)

        if is_ready(url, healthcheck_endpoint, verify):
            break


def is_ready(
    url: str, healthcheck_endpoint: str, verify: Union[bool, str] = True
) -> bool:
    """Check whether the app server is up."""
    try:
        response = requests.get(
            url=f"{url}{healthcheck_endpoint}",
            verify=verify,
            timeout=5,
        )

        if response.status_code != 503 and "Mse-Status" not in response.headers:
            return True
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.SSLError:
        return False
    except requests.exceptions.ConnectionError:
        return False

    return False
