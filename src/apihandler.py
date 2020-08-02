import srcomapi
import logging.config

from logger import DEFAULT_CONFIG

GUR_GAME_ID = "j1l7ojdg"
CATEGORIES = {
    'normal': 'wkp53vdr',
    'hard': '7dgm64d4'
}

logging.config.dictConfig(DEFAULT_CONFIG)
log = logging.getLogger("apihandler")

class ApiHandler():
    """Class that handles returning info from the leaderboard, and checking for new runs."""
    def __init__(self):
        # Caches the newest run's ID on init
        log.debug(f"Creating new ApiHandler instance!")
        self.newest_cached = None
        self.api = srcomapi.SpeedrunCom()
        self.api.debug = 1

    def get_run_id(self, category, name):
        """Retrieves a Give Up Robot SRC (PB) run's ID in the given category name by the given username."""
        pbs = self.api.get(f"users/{name}/personal-bests?embed=game,category")
        for r in pbs:
            if r["game"]["data"]["id"] == GUR_GAME_ID and r["category"]["data"]["id"] == CATEGORIES[category]:
                log.debug(f"Found run in {category} by {name}!")
                return r["run"]["id"]  # done for compatibility reasons and also butt
        return None

    def get_place_from_run_id(self, run_id, category):
        """Returns a run's place given it's ID and category ID"""
        # This shouldn't be this hard. Why is place just not included with runs??
        board = self.api.get(f"leaderboards/{GUR_GAME_ID}/category/{category}")
        for r in board["runs"]:
            if r["run"]["id"] == run_id:
                place = r["place"]
                log.debug(f"Run {run_id} in category {category} has place {place}")
                return place
        return 0 # this could not possibly happen, right?

    def get_user_data(self, user):
        """Get a user's data based on their name."""
        log.debug(f"Returning info for user {user}")
        return self.api.get(f"users/{user}")

    def get_run_data(self, run):
        """Returns a run's data based on its ID."""
        log.debug(f"Returning info for run {run}")
        return self.api.get(f"runs/{run}")

    def check_for_new_run(self):
        """Checks if a run newer than the one cached has been created.
           If one has, then set self.newest_cached to be equal to its ID, and return true."""
        # A very.. special query
        newest_id = self.api.get(f"runs?status=verified&game={GUR_GAME_ID}&orderby=verify-date&direction=desc&embed=category")[0]["id"]
        log.debug(f"Found newest run candidate {newest_id}")
        if newest_id != self.newest_cached and self.newest_cached != None: # if newest_cached is None, that means we just initialized, so there probably isn't actually a new run
            self.newest_cached = newest_id
            return True
        self.newest_cached = newest_id
        return False

    def get_top_run_ids(self, category, n=10):
        """Returns the top 'n' run's IDs in the given category"""
        pass
