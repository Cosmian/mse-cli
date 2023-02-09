"""MSE module."""

import os
import sys
from pathlib import Path

__version__ = "0.10.0"

# This directory contains the login information of the user
# and the context of all its deployments
_DEFAULT_MSE_CONF_DIR = "~/.config"
if sys.platform == "win32":
    _DEFAULT_MSE_CONF_DIR = os.getenv("APPDATA")

MSE_CONF_DIR = (
    Path(os.getenv("MSE_CONF_PATH", _DEFAULT_MSE_CONF_DIR + "/mse/"))
    .expanduser()
    .resolve()
)
os.makedirs(MSE_CONF_DIR, exist_ok=True)

# The URL to get the enclave signing certificate of cosmian
MSE_CERTIFICATES_URL = "https://certificates.cosmian.com/"

# The PCCS to proceed the enclave remote attestation
MSE_PCCS_URL = os.getenv("MSE_PCCS_URL", default="https://pccs.mse.cosmian.com")

# The URL of the mse backend
MSE_BACKEND_URL = os.getenv("MSE_BASE_URL", default="https://backend.mse.cosmian.com")

# The URL of Auth0 login page
MSE_AUTH0_DOMAIN_NAME = os.getenv(
    "MSE_AUTH0_DOMAIN_NAME", default="https://auth.cosmian.com"
)

# The Auth0 client id
MSE_AUTH0_CLIENT_ID = os.getenv(
    "MSE_AUTH0_CLIENT_ID", default="KJtOg5fdA90ZdsaXvM69uME2QD6yP9M3"
)

# The URL of the Auth0 audience
MSE_AUTH0_AUDIENCE = os.getenv(
    "MSE_AUTH0_AUDIENCE", default="https://console-prod.eu.auth0.com/api/v2/"
)

# The URL of the MSE console
MSE_CONSOLE_URL = os.getenv("MSE_CONSOLE_URL", default="https://console.cosmian.com")

# The URL of the default MSE Docker
MSE_DEFAULT_DOCKER = "ghcr.io/cosmian/mse-flask:20230124182826"

# The URL of the MSE documentation
MSE_DOC_URL = "https://docs.cosmian.com/microservice_encryption"

# The URL of the Security model documentation
MSE_DOC_SECURITY_MODEL_URL = f"{MSE_DOC_URL}/security/"
