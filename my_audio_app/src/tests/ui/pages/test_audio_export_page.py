import unittest
import sys
from PyQt6.QtWidgets import QApplication
from my_audio_app.src.ui.pages.audio_export_page import AudioExportPage

class TestAudioExportPage(unittest.TestCase):
    def test_page_creation(self):
        """Test that the AudioExportPage can be created."""
        app = QApplication.instance() or QApplication(sys.argv)
        page = AudioExportPage()
        self.assertIsNotNone(page)

if __name__ == '__main__':
    unittest.main()
