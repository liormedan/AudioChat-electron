import unittest
import sys
import os
from PyQt6.QtWidgets import QApplication

# add src directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..'))
from ui.main_window import MainWindow

class TestMainWindowLLMNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_llm_page_registered(self):
        window = MainWindow()
        self.assertIn('llm_management', window.sidebar.buttons)
        self.assertIn('llm_management', window.pages)

    @classmethod
    def tearDownClass(cls):
        if isinstance(cls.app, QApplication):
            cls.app.quit()

if __name__ == '__main__':
    unittest.main()
