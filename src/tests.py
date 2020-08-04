import unittest
from apihandler import ApiHandler, CATEGORIES, GUR_GAME_ID
from run import format_time, Run
from player import hex_to_rgb, Player

class TestApiHandler(unittest.TestCase):
    def test_init(self):
        api = ApiHandler()
        self.assertEqual(api.newest_cached, None)

    def test_get_run_id(self):
        api = ApiHandler()
        run_id = api.get_run_id("normal", "mashy") # if this guy comes back and gets a new run I guess I have to change this
        self.assertEqual(run_id, "7yl11n2m")
    
    def test_get_run_id_fail(self):
        api = ApiHandler()
        run_id = api.get_run_id("normal", "asdfasd")
        self.assertIsNone(run_id)

    def test_get_place_from_run_id(self):
        api = ApiHandler()
        run_id = api.get_run_id("normal", "mashy")
        place = api.get_place_from_run_id(run_id, CATEGORIES["normal"])
        self.assertGreater(place, 0)

    # now we use a bogus ID
    def test_get_place_from_run_id_badid(self):
        api = ApiHandler()
        place = api.get_place_from_run_id("asdasmwdmaskdoz", CATEGORIES["normal"])
        self.assertEqual(place, 0)

    def test_get_player(self):
        api = ApiHandler()
        user = api.get_player("cyclowns")
        self.assertEqual(user.get_name(), "cyclowns")
    
    def test_get_player_guest(self):
        api = ApiHandler()
        user = api.get_player("btspider")
        self.assertEqual(user.get_name(), "btspider")
    
    def test_get_run(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m") # mashy's run
        self.assertEqual(run.get_game(), GUR_GAME_ID)
    
    def test_get_leaderboard_data(self):
        api = ApiHandler()
        lb_data = api.get_leaderboard_data("normal")
        self.assertEqual(lb_data["game"], GUR_GAME_ID)
    
    def test_check_for_new_run_nonewruns(self):
        api = ApiHandler()
        self.assertFalse(api.check_for_new_run()) # first call always is false since its checking against nothing
        
    def test_check_for_new_run_mocknewrun(self):
        api = ApiHandler()
        api.newest_cached = "mock"
        self.assertTrue(api.check_for_new_run()) # newest_cached and the run found shouldn't be equal now that I've changed it

class TestPlayer(unittest.TestCase):
    """Tests for player.py"""
    def test_hex_to_rgb(self):
        h1 = "#FF0000"
        self.assertEqual(hex_to_rgb(h1), (255, 0, 0))
    
    def test_get_name_guest(self):
        p = Player(None, "bart simpson")
        self.assertEqual(p.get_name(), "bart simpson")
    
    def test_get_name_user(self):
        api = ApiHandler()
        p = api.get_player("cyclowns")
        self.assertEqual(p.get_name(), "cyclowns")
    
    def test_get_colour_guest(self):
        p = Player(None, "woohooboy")
        self.assertEqual(p.get_colour(), hex_to_rgb("#555555"))
    
    def test_get_colour_user(self):
        api = ApiHandler()
        p = api.get_player("cyclowns")
        self.assertIsNotNone(p.get_colour())
    
    def test_get_flag_guest(self):
        p = Player(None, "asphalt")
        self.assertEqual(p.get_flag(), "")
    
    def test_get_flag_province(self):
        api = ApiHandler()
        p = api.get_player("alexbest20")
        self.assertEqual(p.get_flag(), ":flag_ca:")

    def test_get_flag_nolocation(self):
        api = ApiHandler()
        p = api.get_player("KyleKatt") # no location guy, better hope he doesnt add one
        self.assertEqual(p.get_flag(), "")

    def test_get_flag_withlocation(self):
        api = ApiHandler()
        p = api.get_player("cyclowns")
        self.assertEqual(p.get_flag(), ":flag_us:")

class TestRun(unittest.TestCase):
    """Tests for run.py"""
    def test_get_verifier(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        verifier = api.get_player(run.get_verifier())
        self.assertEqual(verifier.get_name(), "zachsk")

    def test_get_runner_id_guest(self):
        api = ApiHandler()
        run = api.get_run("zg73weez")
        self.assertEqual(run.get_runner_id(), "btspider")

    def test_get_runner_id_user(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        self.assertEqual(run.get_runner_id(), "zx7m10x7")

    def test_get_category(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        self.assertEqual(run.get_category(), CATEGORIES["normal"])

    def test_get_date(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        self.assertEqual(run.get_date(), "2013-04-24")

    def test_get_comment_success(self):
        api = ApiHandler()
        run = api.get_run("zn8nx63z")
        self.assertEqual(run.get_comment(), "I had a friend at school beat my score, and every SINGLE day he would go \"Donald Yah beat my score yet?\" and I'm like no, I'm lazy, but INSOMNIA CAN BRING ABOUT GREAT THINGS, especially procrastination. For sleep.")

    def test_get_comment_fail(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        self.assertEqual(run.get_comment(), "")

    def test_get_igt(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        self.assertEqual(run.get_igt(), 325.53)

    def test_get_igt_formatted(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        self.assertEqual(run.get_igt_formatted(), "5:25.530")

    def test_get_link_video(self):
        api = ApiHandler()
        run = api.get_run("7yl11n2m")
        self.assertEqual(run.get_link(), "https://www.youtube.com/watch?v=-hAOk2y_Xe4")

if __name__ == "__main__":
    unittest.main()