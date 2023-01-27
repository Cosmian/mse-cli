"""mse_cli.utils.spinner module."""

import itertools
import sys
import time


class Spinner:
    """Class to wait and print a spinner."""

    def __init__(self, delay: int):
        """Initialize the spinner to wait `delay`."""
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.delay = delay
        self.period = 1

    def wait(self):
        """Wait `self.delay` and print a char every `self.period` seconds."""
        delay = self.delay
        while delay != 0:
            sys.stdout.write(next(self.spinner))  # write the next character
            sys.stdout.flush()  # flush stdout buffer (actual character display)
            sys.stdout.write('\b')  # erase the last written char
            time.sleep(self.period)  # wait for a period time
            delay -= self.period

    def reset(self):
        """Remove the spinner."""
        sys.stdout.write(' ')
        sys.stdout.write('\n')
        sys.stdout.flush()  # flush stdout buffer (actual character display)
