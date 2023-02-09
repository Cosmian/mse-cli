"""mse_cli.utils.spinner module."""

import itertools
import sys
import threading
import time


class Spinner:
    """Class to wait and print a spinner."""

    def __init__(self, message: str):
        """Initialize the spinner."""
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.busy = True
        self.period = 1
        self.message = message

    def __task(self):
        """Make the spinner spin."""
        while self.busy:
            sys.stdout.write(next(self.spinner))  # write the next character
            sys.stdout.flush()  # flush stdout buffer (actual character display)
            sys.stdout.write("\b")  # erase the last written char
            time.sleep(self.period)  # wait for a period time

    def start(self):
        """Start spinning."""
        self.busy = True
        sys.stdout.write(self.message)
        threading.Thread(target=self.__task).start()

    def __enter__(self):
        """Entrypoint of the `with` statement."""
        self.start()
        return self

    def stop(self):
        """Remove the spinner."""
        self.busy = False
        sys.stdout.write(" ")
        sys.stdout.write("\n")
        sys.stdout.flush()  # flush stdout buffer (actual character display)

    def __exit__(self, exception_type, exception_value, traceback):
        """Endpoint of the `with` statement."""
        self.stop()
