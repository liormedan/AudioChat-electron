import os
import tempfile
import shutil
import unittest
from datetime import datetime, timedelta

from services.file_service import FileService
from services.file_stats_data_manager import FileStatsDataManager
from ui.components.file_upload.file_info import FileInfo


class TestFileStatsDataManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "files.db")
        self.file_service = FileService(db_path=self.db_path)
        self.manager = FileStatsDataManager(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_empty_database(self):
        self.assertEqual(self.manager.get_total_files_count(), 0)
        self.assertEqual(self.manager.get_total_duration(), 0)
        self.assertEqual(self.manager.get_format_distribution(), {})
        self.assertIsNone(self.manager.get_last_upload_date())
        self.assertEqual(self.manager.get_recent_files(), [])
        self.assertEqual(self.manager.get_upload_timeline(), {})

    def test_statistics_with_data(self):
        file1 = FileInfo(
            name="a.mp3",
            path="/path/a.mp3",
            size=1000,
            format="mp3",
            duration=60,
            upload_date=datetime.now() - timedelta(days=1),
        )
        file2 = FileInfo(
            name="b.wav",
            path="/path/b.wav",
            size=2000,
            format="wav",
            duration=120,
            upload_date=datetime.now(),
        )
        self.file_service.save_file_info(file1)
        self.file_service.save_file_info(file2)

        self.assertEqual(self.manager.get_total_files_count(), 2)
        self.assertEqual(self.manager.get_total_duration(), 180)
        self.assertEqual(
            self.manager.get_format_distribution(), {"mp3": 1, "wav": 1}
        )
        self.assertAlmostEqual(
            self.manager.get_last_upload_date().date(), file2.upload_date.date()
        )
        self.assertEqual(len(self.manager.get_recent_files()), 2)
        timeline = self.manager.get_upload_timeline(days=2)
        self.assertEqual(sum(timeline.values()), 2)

    def test_connection_error(self):
        bad = FileStatsDataManager(db_path="/invalid/path/db.sqlite")
        self.assertEqual(bad.get_total_files_count(), 0)
        self.assertEqual(bad.get_recent_files(), [])


if __name__ == "__main__":
    unittest.main()

