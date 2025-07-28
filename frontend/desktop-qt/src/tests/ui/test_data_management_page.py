import unittest
import sys
import os
from PyQt6.QtWidgets import QApplication

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..')
)
from ui.pages.data_management_page import DataManagementPage


class TestDataManagementPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_widget_creation(self):
        page = DataManagementPage()
        self.assertIsNotNone(page.local_files_list)
        self.assertIsNotNone(page.s3_files_list)
        self.assertIsNotNone(page.gcs_files_list)
        self.assertIsNotNone(page.azure_files_list)

    @classmethod
    def tearDownClass(cls):
        if isinstance(cls.app, QApplication):
            cls.app.quit()


if __name__ == '__main__':
    unittest.main()
