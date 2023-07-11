"""mse_cli.core.conf module."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import toml
from cryptography import x509
from cryptography.x509.extensions import SubjectAlternativeName
from pydantic import BaseModel, constr, validator

from mse_cli.error import BadApplicationInput

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


class AppConfParsingOption(Enum):
    """Parsing option for AppConf."""

    All = 0
    SkipCloud = 1
    UseInsecureCloud = 2


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


class CloudConf(BaseModel):
    """Define the cloud configuration."""

    # Mse docker to use (containing all requirements)
    docker: StrUnlimited
    # Location of the code
    code: Path
    # Location of the tests
    tests: Path
    # Name of the parent project
    project: Str255
    # MSE hardware (defining the enclave memory, cpu, etc.)
    hardware: Str16
    # The application will stop at this date
    expiration_date: Optional[datetime]
    # Put the configuration in development mode
    dev_mode: bool = False
    # Configuration of the ssl
    ssl: Optional[SSLConf] = None
    # File containing app secrets
    secrets: Optional[Path] = None

    @property
    def secrets_data(self) -> Optional[dict[str, Any]]:
        """Get the data from secrets file."""
        return json.loads(self.secrets.read_text()) if self.secrets else None

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

    def finish_loading(self, path: Path):
        """Proceed extra processings and check from the loaded toml."""
        # Make the app code location path absolute from path.parent and not cwd
        self.code = absolute_from_conf_file(path, self.code)
        self.tests = absolute_from_conf_file(path, self.tests)

        if self.secrets:
            self.secrets = absolute_from_conf_file(path, self.secrets)

        if self.ssl:
            # Make the cert and key location path absolute
            # from path.parent and not cwd
            self.ssl.certificate = absolute_from_conf_file(path, self.ssl.certificate)
            self.ssl.private_key = absolute_from_conf_file(path, self.ssl.private_key)

            cert = x509.load_pem_x509_certificate(
                self.ssl.certificate_data.encode("utf8")
            )

            # Check `expiration_date` using cert expiration date
            if not self.expiration_date:
                self.expiration_date = cert.not_valid_after.replace(tzinfo=timezone.utc)
            elif self.expiration_date > cert.not_valid_after.replace(
                tzinfo=timezone.utc
            ):
                raise BadApplicationInput(
                    f"`expiration_date` ({self.expiration_date}) can't be after "
                    f"the certificate expiration date ({cert.not_valid_after})"
                )

            # Check domain names from cert
            ext = cert.extensions.get_extension_for_class(SubjectAlternativeName)
            domains = ext.value.get_values_for_type(x509.DNSName)

            # Create a wildcard domain from the ssl domain
            wildcard_s = self.ssl.domain_name.split(".")
            wildcard_s[0] = "*"
            wildcard = ".".join(wildcard_s)

            if wildcard not in domains and self.ssl.domain_name not in domains:
                raise BadApplicationInput(
                    f"{self.ssl.domain_name} should be present in the "
                    f"SSL certificate as a Subject Alternative Name ({domains})"
                )

        if self.expiration_date and self.expiration_date <= datetime.now(
            tz=timezone.utc
        ):
            raise BadApplicationInput(
                f"`expiration_date` ({self.expiration_date}) is in the past"
            )


class AppConf(BaseModel):
    """Define the application configuration."""

    # Name of the mse instance
    name: Str255
    # from python_flask_module import python_flask_variable_name
    python_application: Str255
    # Endpoint to use to check if the application is up and sane
    healthcheck_endpoint: Str255
    # The command to test the application
    tests_cmd: str
    # The package to install before testing the application
    tests_requirements: List[str]

    # Extra configuration for mse cloud
    cloud: Optional[CloudConf] = None

    def cloud_or_raise(self) -> CloudConf:
        """Get the cloud configuration or raise if there is none."""
        if not self.cloud:
            raise BadApplicationInput(
                "No `cloud` configuration find in the app configuration"
            )

        return self.cloud

    @validator("healthcheck_endpoint", pre=False)
    # pylint: disable=no-self-argument,unused-argument
    def check_healthcheck_endpoint(cls, v: str):
        """Validate that `healthcheck_endpoint` is an endpoint."""
        if v.startswith("/"):
            return v
        raise ValueError('healthcheck_endpoint should start with a "/"')

    @staticmethod
    def load(
        path: Optional[Path],
        option: AppConfParsingOption = AppConfParsingOption.All,
    ):
        """Load the configuration from a toml file."""
        path = path.expanduser() if path else Path(os.getcwd()) / "mse.toml"

        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

            if option == AppConfParsingOption.SkipCloud:
                dataMap.pop("cloud", None)

            if "cloud" in dataMap:
                dataMap["cloud"]["dev_mode"] = False

                if option == AppConfParsingOption.UseInsecureCloud:
                    dataMap["cloud"].pop("ssl", None)
                    dataMap["cloud"]["dev_mode"] = True

            app = AppConf(**dataMap)
            if app.cloud:
                app.cloud.finish_loading(path)

            return app

    def save(self, path: Path) -> None:
        """Save the configuration into a toml file."""
        with open(path, "w", encoding="utf8") as f:
            dataMap: Dict[str, Any] = {
                "name": self.name,
                "python_application": self.python_application,
                "healthcheck_endpoint": self.healthcheck_endpoint,
                "tests_cmd": self.tests_cmd,
                "tests_requirements": self.tests_requirements,
            }

            if self.cloud:
                cloud: Dict[str, Any] = {
                    "code": str(self.cloud.code),
                    "tests": str(self.cloud.tests),
                    "docker": self.cloud.docker,
                    "project": self.cloud.project,
                    "hardware": self.cloud.hardware,
                }

                if self.cloud.secrets:
                    cloud["secrets"] = str(self.cloud.secrets)

                if self.cloud.expiration_date:
                    cloud["expiration_date"] = str(self.cloud.expiration_date)

                if self.cloud.ssl:
                    cloud["ssl"] = {
                        "domain_name": self.cloud.ssl.domain_name,
                        "private_key": str(self.cloud.ssl.private_key),
                        "certificate": str(self.cloud.ssl.certificate),
                    }

                dataMap["cloud"] = cloud

            toml.dump(dataMap, f)

    @property
    def python_module(self):
        """Get the python module from python_application."""
        split_str = self.python_application.split(":")
        if len(split_str) != 2:
            raise BadApplicationInput(
                "`python_application` is malformed. Expected format: `module:variable`"
            )
        return split_str[0]

    @property
    def python_variable(self):
        """Get the python variable from python_application."""
        split_str = self.python_application.split(":")
        if len(split_str) != 2:
            raise BadApplicationInput(
                "`python_application` is malformed. Expected format: `module:variable`"
            )
        return split_str[1]

    def into_cloud_payload(self) -> Dict[str, Any]:
        """Convert it into a mse-backend payload as a dict."""
        cloud = self.cloud_or_raise()

        d = (
            cloud.expiration_date.astimezone(tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            if cloud.expiration_date
            else None
        )

        return {
            "name": self.name,
            "project": cloud.project,
            "dev_mode": cloud.dev_mode,
            "healthcheck_endpoint": self.healthcheck_endpoint,
            "python_application": self.python_application,
            "expires_at": d,
            "ssl_certificate": cloud.ssl.certificate_data if cloud.ssl else None,
            "domain_name": cloud.ssl.domain_name if cloud.ssl else None,
            "hardware": cloud.hardware,
            "docker": cloud.docker,
        }  # Do not send the private_key or the code location
