"""mse_cli.color module."""


from enum import Enum


class ColorKind(str, Enum):
    """ANSI color codes."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    LINK_START = "\u001b]8;;"
    LINK_MID = "\u001b\\"
    LINK_END = "\u001b]8;;\u001b\\"


class ColorRender:
    """Render class to enable or disable colors."""

    def __init__(self):
        """Initialize the object with color enabled."""
        self.active = True

    @property
    def active(self):
        """Say whether the color is enabled."""
        return self._active

    @active.setter
    def active(self, value: bool):
        """Enable or disable the color."""
        self._active = value

    def render(self, kind: ColorKind) -> str:
        """Render the color or not depending on if it is enabled."""
        return kind.value if self.active else ""


COLOR = ColorRender()


def setup_color(color: bool = True):
    """Configure output coloring."""
    COLOR.active = color
