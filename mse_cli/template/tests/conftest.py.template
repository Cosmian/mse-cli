import os
import socket
import ssl
import tempfile
from pathlib import Path
from typing import Optional, Union

import pytest
from cryptography import x509


@pytest.fixture(scope="module")
def url() -> str:
    return os.getenv("TEST_REMOTE_URL", "http://localhost:5000/")


@pytest.fixture(scope="module")
def workspace() -> Path:
    return Path(tempfile.mkdtemp())


@pytest.fixture(scope="module")
def certificate(url, workspace) -> Union[Path, bool]:
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

    # get server certificate
    pem: Optional[str] = None
    with socket.create_connection((hostname, 443), timeout=10) as sock:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            bin_cert = ssock.getpeercert(True)
            if not bin_cert:
                raise Exception("Can't get peer certificate")
            pem = ssl.DER_cert_to_PEM_cert(bin_cert)

    if pem:
        cert = x509.load_pem_x509_certificate(pem.encode("utf8"))
        if cert.subject == cert.issuer:  # self signed certificate
            # save it for future use
            cert_path.write_bytes(pem.encode("utf-8"))
        else:
            cert_path.write_text("1")
            return True

    return cert_path
