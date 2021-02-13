import srcomapi
import logging.config
from fuzzywuzzy import process

from logger import DEFAULT_CONFIG
from user import User
from run import Run

logging.config.dictConfig(DEFAULT_CONFIG)
log = logging.getLogger("apihandler")


class CategoryLevel():
    """Contains data about a category or level. Rules is nullable"""
    def __init__(self, id, name, rules):
        self.id = id
        self.name = name
        self.rules = rules
        self.newest = None


class ApiHandler():
    """Class that handles returning info from the leaderboard,
    and checking for new runs."""

    def __init__(self, game_id):
        # Caches the newest run's ID on init
        log.debug(f"Creating new ApiHandler instance for game {game_id}!")
        self.game_id = game_id
        self.newest_cached = None
        self.seen_runs = []
        self.api = srcomapi.SpeedrunCom()
        self.api.debug = 1

        self.categories = []
        self.levels = []
        self.populate_categories()
        self.populate_levels()

    def categorylevel_name_from_id(self, id):
        for c in self.categories:
            if c.id == id:
                return c.name
        for l in self.levels:
            if l.id == id:
                return l.name

    def categorylevel_id_from_name(self, name):
        for c in self.categories:
            if c.name == name:
                return c.id
        for l in self.levels:
            if l.name == name:
                return l.id
        return name

    def populate_categories(self):
        """Creates a list self.categories containing Category classes, containing info about the categories."""
        categories = self.api.get(f"games/{self.game_id}/categories")
        for c in categories:
            cat = CategoryLevel(c["id"], c["name"], c["rules"])
            self.categories.append(cat)

    def populate_levels(self):
        """Creates a list self.levels containing Level classes, containing info about the levels."""
        levels = self.api.get(f"games/{self.game_id}/levels")
        for c in levels:
            cat = CategoryLevel(c["id"], c["name"], c["rules"])
            self.levels.append(cat)

    def fuzzy_match_categorylevel(self, text):
        names = []
        for c in self.categories:
            names.append(c.name)
        for l in self.levels:
            names.append(l.name)
        return process.extractOne(text, names)[0]

    def get_run_id(self, category, user):
        """Retrieves a Give Up Robot SRC (PB) run's ID in the given
        category name by the given username."""
        try:
            cat_name = self.fuzzy_match_categorylevel(category)
            leaderboard = self.get_categorylevel_leaderboard(cat_name)
            runs = leaderboard["runs"]
            players = leaderboard["players"]["data"]
            names_by_run = {}
            for r in runs:
                idx = runs.index(r)
                run_data = Run(r["run"])  # run
                try:
                    user_name = players[idx]["names"]["international"]
                except KeyError:
                    continue
                names_by_run[run_data.get_run_id()] = user_name
            name = process.extractOne(user, names_by_run.values())[0]
            log.info(f"Found run in {cat_name} by {name}!")
            # thanks speedrun.com
            return list(names_by_run.keys())[list(names_by_run.values()).index(name)]
        except srcomapi.exceptions.APIRequestException:
            return None

    def get_place_from_run_id(self, run_id, category):
        """Returns a run's place given it's ID and category ID"""
        # This shouldn't be this hard. Why isn't place just included with runs?
        log.debug(f"Getting place for run with ID {run_id} and category/level {category}")
        board = self.get_categorylevel_leaderboard(category)
        for r in board["runs"]:
            potential = r["run"]["id"]
            if potential == run_id:
                place = r["place"]
                log.debug(f"Run {run_id} in category {category} has place {place}")
                return place
        return 0  # this could not possibly happen, right?

    def get_user(self, user):
        """Get a user's data as a User class based on their name,
         or nothing if they're a guest."""
        try:
            p_data = self.api.get(f"users/{user}")
            log.info(f"Returning info for normal user {user}")
            return User(p_data)
        except srcomapi.exceptions.APIRequestException:
            log.info(f"Returning info for guest user {user}")
            return User(None, guest_name=user)

    def get_run(self, run):
        """Returns a run's data as a Run class based on its ID."""
        log.info(f"Returning info for run {run}")
        return Run(self.api.get(f"runs/{run}"))

    def get_categorylevel_leaderboard(self, categorylevel):
        """Gets a category or level's leaderboard data"""
        for c in self.categories:
            if c.name == categorylevel or c.id == categorylevel:
                log.info(f"Returning info for category leaderboard {categorylevel}")
                cat_id = self.categorylevel_id_from_name(categorylevel)
                return self.api.get(f"leaderboards/{self.game_id}/category/{cat_id}?embed=players")
        log.info(f"Returning info for level leaderboard {categorylevel}")
        return self.api.get(f"leaderboards/{self.game_id}/level/{categorylevel}?embed=players")

    def check_for_new_run(self):
        """Checks if a run newer than the one cached has been created.
           If one has, then set self.newest_cached to be equal to its ID,
           and return true."""
        # A very.. special query
        newest_run = self.api.get(f"runs?status=verified&game={self.game_id}&orderby=verify-date&direction=desc&embed=category")
        newest_id = newest_run[0]["id"]
        log.debug(f"Found newest run candidate {newest_id}")

        if newest_id != self.newest_cached and self.newest_cached is not None and newest_id not in self.seen_runs:
            # if newest_cached is None, that means we just initialized,
            # so there probably isn't actually a new run
            self.newest_cached = newest_id
            self.newest_in_categories[newest_run[0]["category"]["data"]["id"]] = newest_id
            self.seen_runs.append(newest_id)
            log.debug(f"Found actual new run {newest_id}!")
            return True

        self.newest_cached = newest_id
        self.newest_in_categories[newest_run[0]["category"]["data"]["id"]] = newest_id
        return False
