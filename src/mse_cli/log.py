"""mse_cli.log module."""

import logging
import sys

from mse_cli.color import COLOR, ColorKind

LOGGER = logging.getLogger("mse")

LOGGING_SUCCESS = 25
LOGGING_ADVICE = 26


class MSEFormatter(logging.Formatter):
    """Logging colored formatter."""

    def __init__(self, fmt):
        """Initialize the formatter."""
        super().__init__()
        self.fmt = fmt
        if COLOR.active:
            self.FORMATS = {
                logging.DEBUG: self.fmt,
                logging.INFO: self.fmt,
                LOGGING_ADVICE: f"{ColorKind.OKBLUE}💡 {self.fmt}{ColorKind.ENDC}",
                LOGGING_SUCCESS: f"{ColorKind.OKGREEN}✅ {self.fmt}{ColorKind.ENDC}",
                logging.WARNING: f"{ColorKind.WARNING}🚨 {self.fmt}{ColorKind.ENDC}",
                logging.ERROR: f"{ColorKind.FAIL}❌ {self.fmt}{ColorKind.ENDC}",
                logging.CRITICAL: f"{ColorKind.FAIL}❌ {self.fmt}{ColorKind.ENDC}",
            }
        else:
            self.FORMATS = {
                logging.DEBUG: self.fmt,
                logging.INFO: self.fmt,
                LOGGING_ADVICE: self.fmt,
                LOGGING_SUCCESS: self.fmt,
                logging.WARNING: self.fmt,
                logging.ERROR: self.fmt,
                logging.CRITICAL: self.fmt,
            }

    def format(self, record):
        """Format the log with color and emojis."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging(debug: bool = False):
    """Configure basic logging."""
    format_msg = "%(message)s"

    # Define a specific format for stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    stdout_handler.setFormatter(MSEFormatter(format_msg))

    logging.basicConfig(format=format_msg, handlers=[stdout_handler])
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)

    # Add a success level to the default logger (then we can write LOG.success("msg"))
    logging.addLevelName(LOGGING_SUCCESS, "SUCCESS")
    # pylint: disable=protected-access
    setattr(
        LOGGER,
        "success",
        lambda message, *args: LOGGER._log(LOGGING_SUCCESS, message, args),
    )

    # Add a advice level to the default logger (then we can write LOG.advice("msg"))
    logging.addLevelName(LOGGING_ADVICE, "ADVICE")
    # pylint: disable=protected-access
    setattr(
        LOGGER,
        "advice",
        lambda message, *args: LOGGER._log(LOGGING_ADVICE, message, args),
    )
