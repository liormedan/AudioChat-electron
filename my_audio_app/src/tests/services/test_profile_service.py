import unittest
import os
import tempfile
from datetime import datetime

from services.profile_service import ProfileService
from models.user_profile import UserProfile


class TestProfileService(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.service = ProfileService(db_path=self.temp_db.name)

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_create_and_get_profile(self):
        profile = UserProfile(
            id="user1",
            display_name="Tester",
            email="tester@example.com",
            avatar_path=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.service.save_profile(profile)
        retrieved = self.service.get_profile("user1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.display_name, profile.display_name)
        self.assertEqual(retrieved.email, profile.email)

    def test_update_profile(self):
        profile = UserProfile(
            id="user1",
            display_name="Tester",
            email="tester@example.com",
            avatar_path=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.service.save_profile(profile)
        profile.display_name = "Updated"
        profile.updated_at = datetime.now()
        self.service.save_profile(profile)
        retrieved = self.service.get_profile("user1")
        self.assertEqual(retrieved.display_name, "Updated")


if __name__ == "__main__":
    unittest.main()
