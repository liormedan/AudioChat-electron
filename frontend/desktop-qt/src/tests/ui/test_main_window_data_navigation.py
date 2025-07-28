import unittest
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# add src directory so that imports work when running tests directly
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..')
)
from ui.main_window import MainWindow
from ui.pages.data_management_page import DataManagementPage


class TestMainWindowDataNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_data_page_registered(self):
        window = MainWindow()
        self.assertIn('data_management', window.sidebar.buttons)
        self.assertIsInstance(window.pages.get('data_management'), DataManagementPage)

    def test_navigation_to_data_page(self):
        window = MainWindow()
        button = window.sidebar.buttons['data_management']
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        self.assertIs(window.stack.currentWidget(), window.pages['data_management'])

    @classmethod
    def tearDownClass(cls):
        if isinstance(cls.app, QApplication):
            cls.app.quit()


if __name__ == '__main__':
    unittest.main()
