import unittest
import os
import db_mgr

class TestDBMgr(unittest.TestCase):
    def setUp(self):
        # Use a test DB
        db_mgr.DB_NAME = "test_magxxic.db"
        if os.path.exists(db_mgr.DB_NAME):
            os.remove(db_mgr.DB_NAME)
        db_mgr.init_db()

    def tearDown(self):
        if os.path.exists(db_mgr.DB_NAME):
            os.remove(db_mgr.DB_NAME)

    def test_save_and_get(self):
        db_mgr.save_domain_provider("example.com", "TestProvider")
        self.assertEqual(db_mgr.get_cached_provider("example.com"), "TestProvider")

    def test_overrides(self):
        db_mgr.save_domain_provider("override.com", "UserProvider", source='user')
        overrides = db_mgr.get_user_overrides()
        self.assertIn("override.com", overrides)
        self.assertEqual(overrides["override.com"], "UserProvider")

if __name__ == "__main__":
    unittest.main()
