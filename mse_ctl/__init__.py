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
