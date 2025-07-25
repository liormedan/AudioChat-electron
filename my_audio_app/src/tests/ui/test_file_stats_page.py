import os
import tempfile
import shutil
import unittest
from datetime import datetime

from PyQt6.QtWidgets import QApplication

from services.file_service import FileService
from services.file_stats_data_manager import FileStatsDataManager
from ui.pages.file_stats_page import FileStatsPage
from ui.components.file_upload.file_info import FileInfo


class TestFileStatsPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "files.db")
        self.service = FileService(db_path=self.db_path)
        self.manager = FileStatsDataManager(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_refresh_data_updates_ui(self):
        info = FileInfo(
            name="test.mp3",
            path="/path/test.mp3",
            size=2048,
            format="mp3",
            duration=60,
            upload_date=datetime.now(),
        )
        self.service.save_file_info(info)

        page = FileStatsPage(data_manager=self.manager)
        page.refresh_data()

        self.assertEqual(page.total_files_label.text(), "1")
        self.assertEqual(page.formats_label.text(), "mp3")
        self.assertEqual(page.recent_files_table.rowCount(), 1)


if __name__ == "__main__":
    unittest.main()

