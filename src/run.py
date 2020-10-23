import logging.config

from logger import DEFAULT_CONFIG

logging.config.dictConfig(DEFAULT_CONFIG)
log = logging.getLogger("run")


def format_time(secs):
    """Yes, I know strftime exists. It did not work."""
    mins = (int(secs / 60))
    lsecs = int(secs % 60)
    ms = round((secs - int(secs)) * 1000)
    if lsecs < 10:
        return f"{mins}:0{lsecs}.{ms}"
    else:
        return f"{mins}:{lsecs}.{ms}"


class Run:
    """Wrapper around run data that implements some nice getter functions
    and opens up the path for caching stuff. Similar to Player."""
    def __init__(self, data):
        self.data = data

    def get_run_id(self):
        return self.data["id"]

    def get_verifier(self):
        """Returns the verifier's player ID."""
        log.debug("Returning verifier")
        return self.data["status"]["examiner"]

    def get_runner_id(self):
        if "id" in self.data["players"][0]:
            log.debug("Returning runner ID")
            return self.data["players"][0]["id"]
        else:
            log.debug("No ID found, returning guest name")
            return self.data["players"][0]["name"]

    def get_game(self):
        log.debug("Returning game")
        return self.data["game"]

    def get_category(self):
        log.debug("Returning category")
        return self.data["category"]

    def get_date(self):
        log.debug("Returning date")
        return self.data["date"]

    def get_comment(self):
        if self.data["comment"] is not None:
            log.debug("Returning comment")
            return self.data["comment"]
        else:
            log.debug("No comment found")
            return ""

    def get_primary_time(self):
        """Returns primary time in seconds."""
        log.debug("Returning primary time")
        return self.data["times"]["primary_t"]

    def get_primary_time_formatted(self):
        return format_time(self.get_primary_time())

    def get_igt(self):
        """Returns the ingame time in seconds."""
        log.debug("Returning IGT")
        return self.data["times"]["ingame_t"]

    def get_igt_formatted(self):
        return format_time(self.get_igt())

    def get_link(self):
        """Returns a link to the video submission,
        or to the SRC weblink if it doesn't exist."""
        if "videos" in self.data:
            log.debug("Returning video")
            return self.data["videos"]["links"][0]["uri"]
        else:
            log.debug("Returning weblink")
            return self.data["weblink"]
