"""mse_ctl module."""

import os
import sys
from pathlib import Path

# This directory contains the login information of the user
# and the context of all its deployments
_DEFAULT_MSE_CONF_DIR = "~/.config"
if sys.platform == 'win32':
    _DEFAULT_MSE_CONF_DIR = os.getenv("APPDATA")

MSE_CONF_DIR = Path(
    os.getenv("MSE_CTL_CONF_PATH",
              _DEFAULT_MSE_CONF_DIR + "/mse-ctl/")).expanduser().resolve()
os.makedirs(MSE_CONF_DIR, exist_ok=True)

# The URL to get the enclave signing certificate of cosmian
MSE_CERTIFICATES_URL = "https://certificates.cosmian.com/"

# The PCCS to proceed the enclave remote attestation
MSE_PCCS_URL = "https://pccs.cosmian.com"

# The location of the docker running on the MSE node
MSE_DOCKER_IMAGE_URL = os.getenv("MSE_CTL_DOCKER_REMOTE_URL",
                                 "gitlab.cosmian.com:5000/core/mse-docker")

# The URL of the mse backend
MSE_BACKEND_URL = os.getenv('MSE_CTL_BASE_URL',
                            default="https://backend.mse.cosmian.com")

# The URL to auth0 login page
MSE_AUTH0_DOMAIN_NAME = os.getenv('MSE_CTL_AUTH0_DOMAIN_NAME',
                                  default="https://console-dev.eu.auth0.com")

# The Auth0 client id
MSE_AUTH0_CLIENT_ID = os.getenv('MSE_CTL_AUTH0_CLIENT_ID',
                                default="bx2WlLrS7qr35iyNqUVTs9jMo834o8mC")

# The URL of the auth0 audiance
MSE_AUTH0_AUDIENCE = os.getenv(
    'MSE_CTL_AUTH0_AUDIENCE',
    default="https://console-dev.eu.auth0.com/api/v2/")

# The URL of the MSE console
MSE_CONSOLE_URL = os.getenv('MSE_CTL_CONSOLE_URL',
                            default="http://localhost:3000")
