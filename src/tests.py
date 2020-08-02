import unittest
from apihandler import ApiHandler, CATEGORIES, GUR_GAME_ID

class TestApiHandler(unittest.TestCase):
    def test_init(self):
        lb = ApiHandler()
        self.assertEqual(lb.newest_cached, None)
    
    def test_get_run_id(self):
        lb = ApiHandler()
        run_id = lb.get_run_id("normal", "mashy") # if this guy comes back and gets a new run I guess I have to change this
        self.assertEqual(run_id, "7yl11n2m")

    # get_place_from_run_id is untested, since i don't know how to mock data for it that would be static

    def test_get_user_data(self):
        lb = ApiHandler()
        user = lb.get_user_data("cyclowns")
        self.assertEqual(user["names"]["international"], "cyclowns")
    
    def test_get_run_data(self):
        lb = ApiHandler()
        run = lb.get_run_data("7yl11n2m") # mashy's run
        self.assertEqual(run["game"], GUR_GAME_ID)
        self.assertEqual(run["category"], CATEGORIES["normal"])
    
    def test_check_for_new_run(self):
        lb = ApiHandler()
        self.assertFalse(lb.check_for_new_run()) # first call always is false since its checking against nothing
        
        lb.newest_cached = "mock"
        self.assertTrue(lb.check_for_new_run()) # newest_cached and the run found shouldn't be equal now that I've changed it
    
    def test_get_top_run_ids(self):
        lb = ApiHandler()
        # UNFINISHED
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()