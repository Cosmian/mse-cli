"""App configuration file module."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import toml
from cryptography import x509
from cryptography.x509.extensions import SubjectAlternativeName
from pydantic import BaseModel, validator


class SSLConf(BaseModel):
    """Definition of the app owner certificate."""

    # The domain name of the app
    domain_name: str
    # The ssl private key
    private_key: str
    # The ssl certificate chain
    certificate: str


class CodeConf(BaseModel):
    """Definition of the code configuration."""

    # Location of the code (a path or an url)
    location: Path
    # Wether the code is encrypted or not
    encrypted: bool
    # from python_flask_module import python_flask_variable_name
    python_application: str
    # Endpoint to use to check if the application is up and sane
    health_check_endpoint: str


class AppConf(BaseModel):
    """Definition of an app by a user."""

    # Name of the mse instance
    name: str
    # Version of the mse instance
    version: str
    # Name of the parent project
    project: str

    # MSE plan (defining the enclave memory, cpu, etc.)
    plan: str

    # Delay before stopping the app
    shutdown_delay: Optional[int] = None

    # Configuration of the code
    code: CodeConf

    # Configuration of the ssl
    ssl: Optional[SSLConf] = None

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
    def from_toml(path: Optional[Path] = None):
        """Build a AppConf object from a Toml file."""
        if not path:
            path = Path(os.getcwd()) / "mse.toml"
        else:
            path = path.expanduser()

        with open(path, encoding="utf8") as f:
            dataMap = toml.load(f)

            app = AppConf(**dataMap)

            # Make the app code location path absolute from path.parent and not cwd
            if not app.code.location.is_absolute():
                app.code.location = (path.parent / app.code.location).resolve()

            if app.ssl:
                cert = x509.load_pem_x509_certificate(
                    app.ssl.certificate.encode('utf8'))

                # Set shutdown_delay using cert expiration date
                delta = cert.not_valid_after - datetime.now()
                if not app.shutdown_delay:
                    app.shutdown_delay = delta.days
                elif app.shutdown_delay > delta.days:
                    raise Exception(
                        "`shutdown_delay` ({shutdown_delay}) can't be bigger "
                        "than the number of days before certificate expiration ({delta})"
                    )

                # Check domain names from cert
                ext = cert.extensions.get_extension_for_class(
                    SubjectAlternativeName)
                domains = ext.value.get_values_for_type(x509.DNSName)

                if app.ssl.domain_name not in domains:
                    raise Exception(
                        "{app.ssl.domain_name} should be present in the "
                        "SSL certificate as a Subject Alternative Name ({domains})"
                    )

            return app

    def save(self, folder: Path):
        """Dump the current object to a file."""
        with open(folder / "mse.toml", "w", encoding="utf8") as f:
            dataMap = {
                "name": self.name,
                "version": self.version,
                "project": self.project,
                "plan": self.plan,
                "code": {
                    "location": str(self.code.location),
                    "encrypted": self.code.encrypted,
                    "python_application": self.code.python_application,
                    "health_check_endpoint": self.code.health_check_endpoint
                },
            }

            if self.shutdown_delay:
                dataMap['shutdown_delay'] = str(self.shutdown_delay)
            if self.ssl:
                dataMap['ssl'] = {
                    "domain_name": self.ssl.domain_name,
                    "private_key": self.ssl.private_key,
                    "certificate": self.ssl.certificate
                }

            toml.dump(dataMap, f)

    @staticmethod
    def default(name: str, code_path: Path):
        """Generate a default configuration."""
        code = CodeConf(location=code_path.expanduser().resolve() / "code",
                        encrypted=True,
                        python_application="app:app",
                        health_check_endpoint="/")

        return AppConf(name=name,
                       version="0.1.0",
                       project="default",
                       plan="free",
                       code=code)

    def into_payload(self):
        """Convert it into a mse-backend payload as a dict."""
        return {
            "name": self.name,
            "version": self.version,
            "project": self.project,
            "encrypted_code": self.code.encrypted,
            "health_check_endpoint": self.code.health_check_endpoint,
            "python_application": self.code.python_application,
            "shutdown_delay": self.shutdown_delay,
            "ssl_certificate": self.ssl.certificate if self.ssl else None,
            "domain_name": self.ssl.domain_name if self.ssl else None,
            "plan": self.plan,
        }  # Do not send the private_key or location code
