"""mse_cli.utils.clock_tick module."""

import time


class ClockTick:
    """Class to monitor the spent time."""

    def __init__(self, period: int, timeout: int, message: str):
        """Initialize the clock."""
        self.elapsed = 0
        self.timeout = timeout
        self.period = period
        self.message = message

    def tick(self) -> bool:
        """Start ticking."""
        if self.elapsed > self.timeout:
            raise Exception(self.message)

        time.sleep(self.period)
        self.elapsed += self.period

        return True
