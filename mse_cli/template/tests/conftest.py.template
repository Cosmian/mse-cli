from pathlib import Path
import socket
import ssl
import tempfile
from typing import Optional
import pytest
import os


@pytest.fixture(scope="module")
def url() -> str:
    return os.getenv("TEST_REMOTE_URL", "http://localhost:5000/")


@pytest.fixture(scope="module")
def certificate(url) -> Optional[Path]:
    if "https" not in url:
        return None

    if "localhost" in url:
        return None

    hostname = url.split("https://")[-1]
    cert_path: Path = Path(tempfile.gettempdir()) / "cert.pem"

    if not cert_path.exists():
        # get server certificate
        cert: Optional[str] = None
        with socket.create_connection((hostname, 443)) as sock:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                bin_cert = ssock.getpeercert(True)
                if not bin_cert:
                    raise Exception("Can't get peer certificate")
                cert = ssl.DER_cert_to_PEM_cert(bin_cert)
        if cert:
            # save it for future use
            cert_path.write_bytes(cert.encode("utf-8"))

    return cert_path
