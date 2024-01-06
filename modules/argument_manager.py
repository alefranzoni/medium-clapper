
"""Module to handle all related to arguments."""
import argparse
from enum import Enum

class ArgumentOptions(Enum):
    """Enum class for command line argument options. Defines the available argument options."""
    TARGET = "t"
    SCROLL_DELAY = "sd"
    SCROLL_RETRIES = "sr"
    CLAPS = "c"
    READ_TIME = "rt"
    GENERATE_KEY = "gk"

class ArgumentManager():
    """Class responsible for managing command line arguments."""

    def __init__(self):
        """Initializes the instance by parsing command line arguments."""
        self.args = self._parse()

    def _parse(self):
        """Get the command line arguments passed by the user at runtime."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", metavar="USERNAME", type=str, required=True, help="target username (including '@' if needed)")
        parser.add_argument("-sd", metavar="SCROLL_DELAY", type=float, default=.85, help="add a delay (in seconds) to the scrolling process. Default is 0.85")
        parser.add_argument("-sr", metavar="SCROLL_RETRIES", type=int, default=3, help="add attempts to the scrolling process. Default is 3")
        parser.add_argument("-c", metavar="CLAPS", type=int, default=50, help="number of claps to give on each article. Default is 50")
        parser.add_argument("-rt", metavar="READ_TIME", type=float, default=10, help="time (in seconds) to wait in article to emulate reading time. Default is 10")
        group = parser.add_argument_group("security options")
        group.add_argument("-gk", action="store_true", default=False, help="generate a new passkey to protect PII data")

        return parser.parse_args()

    def get(self, argument: ArgumentOptions):
        """Retrieves the value of a specific argument."""
        return getattr(self.args, argument.value)
