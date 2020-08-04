import logging.config

from logger import DEFAULT_CONFIG

logging.config.dictConfig(DEFAULT_CONFIG)
log = logging.getLogger("player")


def hex_to_rgb(h):
    """Converts a hexcode like `#FABD12` to an RGB triple."""
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class Player:
    """Wrapper around player data that implements some nice getter functions
    and opens up the path for caching stuff. Player.data is nullable."""
    def __init__(self, data, guest_name=None):
        log.debug(f"Creating new {'guest' if guest_name else 'regular'} Player instance!")
        self.data = data
        self.guest_name = guest_name

    def get_name(self):
        """Returns a user's name."""
        if self.guest_name:
            return self.guest_name
        return self.data["names"]["international"]

    def get_colour(self):
        """Returns a user's start gradient color as an RGB tuple."""
        if self.guest_name:
            log.debug("Returning color")
            return hex_to_rgb("#555555")
        log.debug("Returning color")
        return hex_to_rgb(self.data["name-style"]["color-from"]["dark"])

    def get_flag(self):
        """Returns a text string formatted as a discord emoji
        corresponding to the player's country's flag."""
        if self.guest_name or self.data["location"] is None:
            log.debug("No flag found!")
            return ""
        country_code = self.data["location"]["country"]["code"]
        # if it contains a /, then its a code like ca/qc (quebec),
        # or a province (sorta) code, which wont work with discord
        if "/" in country_code:
            log.debug("Invalid province flag, falling back to country flag")
            return f":flag_{country_code[:2]}:"
        else:
            log.debug(f"Returning flag for country {country_code}")
            return f":flag_{country_code}:"
