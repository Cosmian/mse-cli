"""Conftest."""

import os
import tempfile
from pathlib import Path
from typing import Union

import pytest
from cryptography import x509
from intel_sgx_ra.ratls import get_server_certificate


@pytest.fixture(scope="module")
def url() -> str:
    """Get the url of the mse app."""
    return os.getenv("TEST_REMOTE_URL", "http://localhost:5000/")


@pytest.fixture(scope="module")
def workspace() -> Path:
    """Get the path of the test work directory."""
    return Path(tempfile.mkdtemp())


@pytest.fixture(scope="module")
def certificate(url, workspace) -> Union[Path, bool]:
    """Get the mse app certificate."""
    if "https" not in url:
        return False  # Do not check

    if "localhost" in url:
        return False  # Do not check

    hostname = url.split("https://")[-1]
    cert_path: Path = workspace / "cert.pem"

    if cert_path.exists():
        if cert_path.read_text() == "1":
            return True  # Use the ssl bundle from the system
        return cert_path  # Use this specific bundle

    pem = get_server_certificate((hostname, 443))
    cert = x509.load_pem_x509_certificate(pem.encode("utf8"))
    if cert.subject == cert.issuer:  # self signed certificate
        # save it for future use
        cert_path.write_bytes(pem.encode("utf-8"))
    else:
        cert_path.write_text("1")
        return True

    return cert_path
