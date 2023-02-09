"""mse_cli.conf.app module."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

import toml
from cryptography import x509
from cryptography.x509.extensions import SubjectAlternativeName
from pydantic import BaseModel, PrivateAttr, constr, validator

if TYPE_CHECKING:
    Str255 = str
    Str16 = str
    StrUnlimited = str
else:
    Str255 = constr(min_length=1, max_length=255, strip_whitespace=True)
    Str16 = constr(min_length=1, max_length=16, strip_whitespace=True)
    StrUnlimited = constr(min_length=1)


def absolute_from_conf_file(conf_file: Path, path: Path) -> Path:
    """Make the `path` absolute from `conf_file.parent`."""
    if not path.is_absolute():
        return (conf_file.parent / path).resolve()

    return path


class SSLConf(BaseModel):
    """Definition of the app owner certificate."""

    # The domain name of the app
    domain_name: Str255
    # The path to the ssl private key
    private_key: Path
    # The path to the ssl certificate chain
    certificate: Path

    @property
    def certificate_data(self) -> str:
        """Get the data from certificate file."""
        return self.certificate.read_text()

    @property
    def private_key_data(self) -> str:
        """Get the data from private_key file."""
        return self.private_key.read_text()


class CodeConf(BaseModel):
    """Definition of the code configuration."""

    # Location of the code (a path or an url)
    location: Path
    # from python_flask_module import python_flask_variable_name
    python_application: Str255
    # Endpoint to use to check if the application is up and sane
    healthcheck_endpoint: Str255
    # Mse docker to use (containing all requirements)
    docker: StrUnlimited
    # File containing app secrets
    secrets: Optional[Path] = None

    @property
    def secrets_data(self) -> Optional[dict[str, Any]]:
        """Get the data from secrets file."""
        return json.loads(self.secrets.read_text()) if self.secrets else None

    @validator("healthcheck_endpoint", pre=False)
    # pylint: disable=no-self-argument,unused-argument
    def check_healthcheck_endpoint(cls, v: str):
        """Validate that `healthcheck_endpoint` is an endpoint."""
        if v.startswith("/"):
            return v
        raise ValueError('healthcheck_endpoint should start with a "/"')


class AppConf(BaseModel):
    """Definition of an app by a user."""

    # Name of the mse instance
    name: Str255
    # Name of the parent project
    project: Str255
    # MSE resource (defining the enclave memory, cpu, etc.)
    resource: Str16
    # The application will stop at this date
    expiration_date: Optional[datetime]
    # Configuration of the code
    code: CodeConf
    # Configuration of the ssl
    ssl: Optional[SSLConf] = None

    # Enable untrusted ssl (ignore from pydantic)
    _untrusted_ssl: bool = PrivateAttr(default=False)

    @property
    def untrusted_ssl(self) -> bool:
        """Get the _untrusted_ssl."""
        return self._untrusted_ssl

    @validator("expiration_date", pre=False, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def set_expiration_date(cls, v, values, **kwargs) -> Optional[datetime]:
        """Set timezone for expiration_date from a value for pydantic."""
        if not v:
            return None

        if isinstance(v, datetime):
            if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
                # If no timezone, use the local one
                return v.astimezone()

        return v

    @property
    def python_module(self):
        """Get the python module from python_application."""
        split_str = self.code.python_application.split(":")
        if len(split_str) != 2:
            raise Exception(
                "`python_application` is malformed. Expected format: `module:variable`"
            )
        return split_str[0]

    @property
    def python_variable(self):
        """Get the python variable from python_application."""
        split_str = self.code.python_application.split(":")
        if len(split_str) != 2:
            raise Exception(
                "`python_application` is malformed. Expected format: `module:variable`"
            )
        return split_str[1]

    @property
    def app_identifier(self):
        """Get the app identifier."""
        return f"{self.name}"

    @staticmethod
    def from_toml(path: Optional[Path] = None, ignore_ssl: bool = False) -> AppConf:
        """Build a AppConf object from a Toml file."""
        if not path:
            path = Path(os.getcwd()) / "mse.toml"
        else:
            path = path.expanduser()

        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

            if ignore_ssl:
                dataMap["ssl"] = None

            app = AppConf(**dataMap)
            app._untrusted_ssl = ignore_ssl  # pylint: disable=protected-access

            # Make the app code location path absolute from path.parent and not cwd
            app.code.location = absolute_from_conf_file(path, app.code.location)

            if app.code.secrets:
                app.code.secrets = absolute_from_conf_file(path, app.code.secrets)

            if app.ssl:
                # Make the cert and key location path absolute
                # from path.parent and not cwd
                app.ssl.certificate = absolute_from_conf_file(path, app.ssl.certificate)
                app.ssl.private_key = absolute_from_conf_file(path, app.ssl.private_key)

                cert = x509.load_pem_x509_certificate(
                    app.ssl.certificate_data.encode("utf8")
                )

                # Check `expiration_date` using cert expiration date
                if not app.expiration_date:
                    app.expiration_date = cert.not_valid_after.replace(
                        tzinfo=timezone.utc
                    )
                elif app.expiration_date > cert.not_valid_after.replace(
                    tzinfo=timezone.utc
                ):
                    raise Exception(
                        f"`expiration_date` ({app.expiration_date}) can't be after "
                        f"the certificate expiration date ({cert.not_valid_after})"
                    )

                # Check domain names from cert
                ext = cert.extensions.get_extension_for_class(SubjectAlternativeName)
                domains = ext.value.get_values_for_type(x509.DNSName)

                # Create a wildcard domain from the ssl domain
                wildcard_s = app.ssl.domain_name.split(".")
                wildcard_s[0] = "*"
                wildcard = ".".join(wildcard_s)

                if wildcard not in domains and app.ssl.domain_name not in domains:
                    raise Exception(
                        f"{app.ssl.domain_name} should be present in the "
                        f"SSL certificate as a Subject Alternative Name ({domains})"
                    )

            if app.expiration_date and app.expiration_date <= datetime.now(
                tz=timezone.utc
            ):
                raise Exception(
                    f"`expiration_date` ({app.expiration_date}) is in the past"
                )

            return app

    def save(self, folder: Path) -> None:
        """Dump the current object to a file."""
        with open(folder / "mse.toml", "w", encoding="utf8") as f:
            code = {
                "location": str(self.code.location),
                "docker": self.code.docker,
                "python_application": self.code.python_application,
                "healthcheck_endpoint": self.code.healthcheck_endpoint,
            }

            if self.code.secrets:
                code["secrets"] = str(self.code.secrets)

            dataMap: Dict[str, Any] = {
                "name": self.name,
                "project": self.project,
                "resource": self.resource,
                "code": code,
            }

            if self.expiration_date:
                dataMap["expiration_date"] = str(self.expiration_date)
            if self.ssl:
                dataMap["ssl"] = {
                    "domain_name": self.ssl.domain_name,
                    "private_key": str(self.ssl.private_key),
                    "certificate": str(self.ssl.certificate),
                }

            toml.dump(dataMap, f)

    def into_payload(self) -> Dict[str, Any]:
        """Convert it into a mse-backend payload as a dict."""
        d = (
            self.expiration_date.astimezone(tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            if self.expiration_date
            else None
        )

        return {
            "name": self.name,
            "project": self.project,
            "dev_mode": self.untrusted_ssl,
            "healthcheck_endpoint": self.code.healthcheck_endpoint,
            "python_application": self.code.python_application,
            "expires_at": d,
            "ssl_certificate": self.ssl.certificate_data if self.ssl else None,
            "domain_name": self.ssl.domain_name if self.ssl else None,
            "plan": self.resource,
            "docker": self.code.docker,
        }  # Do not send the private_key or code location
