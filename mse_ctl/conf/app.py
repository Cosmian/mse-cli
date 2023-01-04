"""mse_ctl.conf.app module."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

import toml
from cryptography import x509
from cryptography.x509.extensions import SubjectAlternativeName
from pydantic import BaseModel, constr, validator

if TYPE_CHECKING:
    Str255 = str
    Str16 = str
    StrUnlimited = str
else:
    Str255 = constr(min_length=1, max_length=255, strip_whitespace=True)
    Str16 = constr(min_length=1, max_length=16, strip_whitespace=True)
    StrUnlimited = constr(min_length=1)


class SSLConf(BaseModel):
    """Definition of the app owner certificate."""

    # The domain name of the app
    domain_name: Str255
    # The ssl private key
    private_key: StrUnlimited
    # The ssl certificate chain
    certificate: StrUnlimited


class CodeConf(BaseModel):
    """Definition of the code configuration."""

    # Location of the code (a path or an url)
    location: Path
    # from python_flask_module import python_flask_variable_name
    python_application: Str255
    # Endpoint to use to check if the application is up and sane
    health_check_endpoint: Str255


class AppConf(BaseModel):
    """Definition of an app by a user."""

    # Name of the mse instance
    name: Str255
    # Version of the mse instance
    version: Str16
    # Name of the parent project
    project: Str255

    # MSE plan (defining the enclave memory, cpu, etc.)
    plan: Str16

    # Dev mode
    dev: bool = False

    # The application will stop at this date
    expiration_date: Optional[datetime]

    # Configuration of the code
    code: CodeConf

    # Configuration of the ssl
    ssl: Optional[SSLConf] = None

    @validator('expiration_date', pre=False, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def set_expiration_date(cls, v, values, **kwargs) -> Optional[datetime]:
        """Set timezone for expiration_date from a value for pydantic."""
        if not v:
            return None

        d: datetime = v
        if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
            # If no timezone, use the local one
            return d.astimezone()

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
    def service_identifier(self):
        """Get the service identifier."""
        return f"{self.name}-{self.version}"

    @staticmethod
    def from_toml(path: Optional[Path] = None) -> AppConf:
        """Build a AppConf object from a Toml file."""
        if not path:
            path = Path(os.getcwd()) / "mse.toml"
        else:
            path = path.expanduser()

        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

            app = AppConf(**dataMap)

            if app.dev and app.ssl:
                raise Exception("`ssl` param is not allowed when `dev` is true")

            # Make the app code location path absolute from path.parent and not cwd
            if not app.code.location.is_absolute():
                app.code.location = (path.parent / app.code.location).resolve()

            if app.ssl:
                cert = x509.load_pem_x509_certificate(
                    app.ssl.certificate.encode('utf8'))

                # Check `expiration_date` using cert expiration date
                if not app.expiration_date:
                    app.expiration_date = cert.not_valid_after.replace(
                        tzinfo=timezone.utc)
                elif app.expiration_date > cert.not_valid_after.replace(
                        tzinfo=timezone.utc):
                    raise Exception(
                        f"`expiration_date` ({app.expiration_date}) can't be after "
                        f"the certificate expiration date ({cert.not_valid_after})"
                    )

                # Check domain names from cert
                ext = cert.extensions.get_extension_for_class(
                    SubjectAlternativeName)
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
                    tz=timezone.utc):
                raise Exception(
                    f"`expiration_date` ({app.expiration_date}) is in the past")

            return app

    def save(self, folder: Path) -> None:
        """Dump the current object to a file."""
        with open(folder / "mse.toml", "w", encoding="utf8") as f:
            dataMap: Dict[str, Any] = {
                "name": self.name,
                "version": self.version,
                "project": self.project,
                "plan": self.plan,
                "code": {
                    "location": str(self.code.location),
                    "python_application": self.code.python_application,
                    "health_check_endpoint": self.code.health_check_endpoint
                },
            }

            if self.dev:
                dataMap['dev'] = self.dev
            if self.expiration_date:
                dataMap['expiration_date'] = str(self.expiration_date)
            if self.ssl:
                dataMap['ssl'] = {
                    "domain_name": self.ssl.domain_name,
                    "private_key": self.ssl.private_key,
                    "certificate": self.ssl.certificate
                }

            toml.dump(dataMap, f)

    @staticmethod
    def default(name: str, code_path: Path) -> AppConf:
        """Generate a default configuration."""
        code = CodeConf(location=code_path.expanduser().resolve() / "code",
                        python_application="app:app",
                        health_check_endpoint="/")

        return AppConf(name=name,
                       version="0.1.0",
                       project="default",
                       plan="free",
                       code=code)

    def into_payload(self) -> Dict[str, Any]:
        """Convert it into a mse-backend payload as a dict."""
        d = None
        if self.expiration_date:
            d = self.expiration_date.astimezone(
                tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return {
            "name": self.name,
            "version": self.version,
            "project": self.project,
            "dev_mode": self.dev,
            "health_check_endpoint": self.code.health_check_endpoint,
            "python_application": self.code.python_application,
            "expires_at": d,
            "ssl_certificate": self.ssl.certificate if self.ssl else None,
            "domain_name": self.ssl.domain_name if self.ssl else None,
            "plan": self.plan,
        }  # Do not send the private_key or location code
