import unittest
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# add src directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..'))
from ui.main_window import MainWindow
from ui.pages.auth_settings_page import AuthSettingsPage


class TestMainWindowAuthNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_auth_page_registered(self):
        window = MainWindow()
        self.assertIn('auth', window.sidebar.buttons)
        self.assertIsInstance(window.pages.get('auth'), AuthSettingsPage)

    def test_navigation_to_auth_page(self):
        window = MainWindow()
        button = window.sidebar.buttons['auth']
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        self.assertIs(window.stack.currentWidget(), window.pages['auth'])

    @classmethod
    def tearDownClass(cls):
        if isinstance(cls.app, QApplication):
            cls.app.quit()


if __name__ == '__main__':
    unittest.main()
