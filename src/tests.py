import unittest
from apihandler import ApiHandler, CATEGORIES, GUR_GAME_ID

class TestApiHandler(unittest.TestCase):
    def test_init(self):
        api = ApiHandler()
        self.assertEqual(api.newest_cached, None)
    
    def test_get_run_id(self):
        api = ApiHandler()
        run_id = api.get_run_id("normal", "mashy") # if this guy comes back and gets a new run I guess I have to change this
        self.assertEqual(run_id, "7yl11n2m")

    def test_get_place_from_run_id(self):
        api = ApiHandler()
        run_id = api.get_run_id("normal", "mashy")
        place = api.get_place_from_run_id(run_id, CATEGORIES["normal"])
        self.assertGreater(place, 0)

        # now we use a bogus ID
        place = api.get_place_from_run_id("asdasmwdmaskdoz", CATEGORIES["normal"])
        self.assertEqual(place, 0)

    def test_get_user_data(self):
        api = ApiHandler()
        user = api.get_user_data("cyclowns")
        self.assertEqual(user["names"]["international"], "cyclowns")
    
    def test_get_run_data(self):
        api = ApiHandler()
        run = api.get_run_data("7yl11n2m") # mashy's run
        self.assertEqual(run["game"], GUR_GAME_ID)
        self.assertEqual(run["category"], CATEGORIES["normal"])
    
    def test_check_for_new_run(self):
        api = ApiHandler()
        self.assertFalse(api.check_for_new_run()) # first call always is false since its checking against nothing
        
        api.newest_cached = "mock"
        self.assertTrue(api.check_for_new_run()) # newest_cached and the run found shouldn't be equal now that I've changed it
    
    def test_get_top_run_ids(self):
        api = ApiHandler()
        # UNFINISHED
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()