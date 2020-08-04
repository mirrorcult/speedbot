import srcomapi
import logging.config

from logger import DEFAULT_CONFIG
from player import Player
from run import Run

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
        try:
            pbs = self.api.get(f"users/{name}/personal-bests?embed=game,category")
            for r in pbs:
                if r["game"]["data"]["id"] == GUR_GAME_ID and r["category"]["data"]["id"] == CATEGORIES[category]:
                    log.info(f"Found run in {category} by {name}!")
                    return r["run"]["id"]  # done for compatibility reasons and also butt
        except:
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

    def get_player(self, user):
        """Get a user's data as a Player class based on their name, or nothing if they're a guest."""
        try:
            p_data = self.api.get(f"users/{user}")
            log.info(f"Returning info for normal user {user}")
            return Player(p_data)
        except:
            log.info(f"Returning info for guest user {user}")
            return Player(None, guest_name=user)

    def get_run(self, run):
        """Returns a run's data as a Run class based on its ID."""
        log.info(f"Returning info for run {run}")
        return Run(self.api.get(f"runs/{run}"))
    
    def get_leaderboard_data(self, category_name):
        """Gets a category's leaderboard data based on its name."""
        cat_id = CATEGORIES[category_name]
        log.info(f"Returning info for leaderboard {category_name}")
        return self.api.get(f"leaderboards/{GUR_GAME_ID}/category/{cat_id}")

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