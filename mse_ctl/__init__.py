"""mse_ctl module."""

import os
import sys
from pathlib import Path

__version__ = "0.3.6"

# This directory contains the login information of the user
# and the context of all its deployments
_DEFAULT_MSE_CONF_DIR = "~/.config"
if sys.platform == "win32":
    _DEFAULT_MSE_CONF_DIR = os.getenv("APPDATA")

MSE_CONF_DIR = Path(
    os.getenv("MSE_CTL_CONF_PATH",
              _DEFAULT_MSE_CONF_DIR + "/mse-ctl/")).expanduser().resolve()
os.makedirs(MSE_CONF_DIR, exist_ok=True)

# The URL to get the enclave signing certificate of cosmian
MSE_CERTIFICATES_URL = "https://certificates.cosmian.com/"

# The PCCS to proceed the enclave remote attestation
MSE_PCCS_URL = "https://pccs.cosmian.com"

# The URL of the mse backend
MSE_BACKEND_URL = os.getenv("MSE_CTL_BASE_URL",
                            default="https://backend.staging.mse.cosmian.com")

# The URL of Auth0 login page
MSE_AUTH0_DOMAIN_NAME = os.getenv(
    "MSE_CTL_AUTH0_DOMAIN_NAME",
    default="https://mse-console-test.eu.auth0.com")

# The Auth0 client id
MSE_AUTH0_CLIENT_ID = os.getenv("MSE_CTL_AUTH0_CLIENT_ID",
                                default="Vm94ZbQn7fFpf5IbA6511S8yp3DQeau2")

# The URL of the Auth0 audience
MSE_AUTH0_AUDIENCE = os.getenv(
    "MSE_CTL_AUTH0_AUDIENCE",
    default="https://mse-console-test.eu.auth0.com/api/v2/")

# The URL of the MSE console
MSE_CONSOLE_URL = os.getenv("MSE_CTL_CONSOLE_URL",
                            default="https://console.staging.mse.cosmian.com")

# The URL of the default MSE Docker
MSE_DEFAULT_DOCKER = "ghcr.io/cosmian/mse-pytorch:20230104085621"
