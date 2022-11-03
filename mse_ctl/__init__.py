"""mse_ctl module."""

import os
from pathlib import Path

# TODO: deal with Windows and so on
# TODO: create $MSE_CTL_CONF_PATH if not exist
MSE_CONF_DIR = Path(os.getenv("MSE_CTL_CONF_PATH",
                              "~/.config/mse-ctl/")).expanduser()
MSE_CERTIFICATES_URL = "https://certificates.cosmian.com/"
MSE_PCCS_URL = "https://pccs.cosmian.com"
MSE_DOCKER_IMAGE_URL = os.getenv("MSE_CTL_DOCKER_REMOTE_URL",
                                 "gitlab.cosmian.com:5000/core/mse-docker")
MSE_BACKEND_URL = os.getenv('MSE_CTL_BASE_URL',
                            default="https://backend.mse.cosmian.com")
