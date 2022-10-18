"""mse_ctl module."""

import os

from pathlib import Path

# TODO: deal with Windows and so on
MSE_CONF_DIR = Path(os.getenv('MSE_CTL_CONF_PATH', "~/.mce-ctl/")).expanduser()