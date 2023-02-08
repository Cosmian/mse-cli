"""mse_cli.utils.clock_tick module."""

import time


class ClockTick:
    """Class to compute spent time for infinity loop."""

    def __init__(self, period: int, timeout: int, message: str):
        """Initialize the spinner."""
        self.elapsed = 0
        self.timeout = timeout
        self.period = period
        self.message = message

    def tick(self) -> bool:
        """Start spinning."""
        if self.elapsed > self.timeout:
            raise Exception(self.message)

        time.sleep(self.period)
        self.elapsed += self.period

        return True
