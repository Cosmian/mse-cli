"""mse_cli.utils.spinner module."""

import itertools
import sys
import time
import threading


class Spinner:
    """Class to wait and print a spinner."""

    def __init__(self):
        """Initialize the spinner."""
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.busy = True
        self.period = 1

    def __task(self):
        """Make the spinner spin."""
        while self.busy:
            sys.stdout.write(next(self.spinner))  # write the next character
            sys.stdout.flush()  # flush stdout buffer (actual character display)
            sys.stdout.write('\b')  # erase the last written char
            time.sleep(self.period)  # wait for a period time

    def start(self, message):
        """Start spinning."""
        self.busy = True
        sys.stdout.write(message)
        threading.Thread(target=self.__task).start()

    def stop(self):
        """Remove the spinner."""
        self.busy = False
        sys.stdout.write(' ')
        sys.stdout.write('\n')
        sys.stdout.flush()  # flush stdout buffer (actual character display)
