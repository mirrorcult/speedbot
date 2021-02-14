import srcomapi
import logging.config
from fuzzywuzzy import process

from logger import DEFAULT_CONFIG
from user import User
from run import Run

logging.config.dictConfig(DEFAULT_CONFIG)
log = logging.getLogger("game")


class CategoryLevel():
    """Contains data about a category or level. Rules is nullable"""
    def __init__(self, id, name, rules):
        self.id = id
        self.name = name
        self.rules = rules
        self.newest = None


class Game():
    """Handles returning info from a game's leaderboard,
    checking for new runs, and returning other data."""
    def __init__(self, game_id):
        # Caches the newest run's ID on init
        log.debug(f"Creating new Game instance for game {game_id}!")
        self.newest_cached = None
        self.seen_runs = []
        self.api = srcomapi.SpeedrunCom()
        self.api.debug = 1

        self.set_game(game_id)

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

    def set_game(self, game_id):
        """Sets the current game ID/name to game for use with the API, and
        updates categories respectively. game_id can also technically
        be the name of the game on SRC (e.g. smb1, celeste, tein)"""

        # we can't -just- set it to game_id because it could be a soft-ID
        # like celeste, smb1, tein etc
        # and soft IDs work fine for most things, but NOT FOR /run?game={game_id}
        # so fuck you SRC, I have to make it an actual ID
        game_data = self.api.get(f"games/{game_id}")
        self.game_id = game_data["id"]
        self.name = game_data["names"]["international"]
        self.abbreviation = game_data["abbreviation"]
        self.created_time = game_data["created"]

        log.info(f"Successfully set game to {self.game_id} ({self.name}, {self.abbreviation})")
        self.populate_categories_and_levels()

    def populate_categories_and_levels(self):
        """Creates lists self.categories and self.levels containing CategoryLevel
        classes, which contain info about the categories/levels in the game."""
        log.debug(f"Repopulating categories/levels for {self.game_id}")
        categories = self.api.get(f"games/{self.game_id}/categories")
        self.categories = []
        for c in categories:
            cat = CategoryLevel(c["id"], c["name"], c["rules"])
            self.categories.append(cat)

        levels = self.api.get(f"games/{self.game_id}/levels")
        self.levels = []
        for c in levels:
            cat = CategoryLevel(c["id"], c["name"], c["rules"])
            self.levels.append(cat)

    def fuzzy_match_categorylevel(self, text):
        """Returns the closest match to text contained in the names of
        the categories/levels for the current game"""
        names = []
        for c in self.categories:
            names.append(c.name)
        for l in self.levels:
            names.append(l.name)
        result = process.extractOne(text, names)
        log.info(f"Matched '{text}' to '{result[0]}' with {result[1]}% confidence")
        return result[0]

    def get_run_id(self, category, user):
        """Retrieves a run's ID in the given
        category name by the given user."""
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
            result = process.extractOne(user, names_by_run.values())
            log.info(f"Found run by and matched user {user} to {result[0]} with {result[1]}% confidence")
            # thanks speedrun.com
            return list(names_by_run.keys())[list(names_by_run.values()).index(result[0])]
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

    def get_number_of_runners(self):
        # if this doesnt give the right data its because self.game_id
        # is the abbreviation and not the real game ID
        runs = self.api.get(f"runs?status=verified&game={self.game_id}")
        return runs.length()

    def get_run_with_place(self, category, place):
        leaderboard = self.get_categorylevel_leaderboard(self.fuzzy_match_categorylevel(category))
        # I'm aware this is unoptimized but I'm lazy ill fix it later
        for r in leaderboard["runs"]:
            potential = r["place"]
            if potential == place:
                log.debug(f"Run with place {place} in {category} is {r['run']['id']}")
                return r["run"]["id"]
        # nothing found
        return None
