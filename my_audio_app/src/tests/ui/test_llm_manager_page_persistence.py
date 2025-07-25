import unittest
import tempfile
import os

from PyQt6.QtWidgets import QApplication

from services.settings_service import SettingsService
from services.llm_service import LLMService

import ui.pages.llm_manager_page as llm_page_module


class TestLLMManagerPagePersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.temp_settings = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_llm = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_settings.close()
        self.temp_llm.close()

        self.settings_service = SettingsService(db_path=self.temp_settings.name)
        self.llm_service = LLMService(db_path=self.temp_llm.name)

        llm_page_module.settings_service = self.settings_service
        llm_page_module.llm_service = self.llm_service

    def tearDown(self):
        for path in [self.temp_settings.name, self.temp_llm.name]:
            if os.path.exists(path):
                os.unlink(path)

    def test_settings_and_providers_persist(self):
        page1 = llm_page_module.LLMManagerPage()
        page1.current_parameters = {
            "temperature": 0.5,
            "max_tokens": 150,
            "top_p": 0.75,
            "frequency_penalty": 0.1,
        }
        page1._save_settings()

        provider = self.llm_service.get_provider("OpenAI")
        provider.is_connected = True
        provider.api_key = "key-123"
        self.llm_service.save_provider(provider)

        page2 = llm_page_module.LLMManagerPage()
        self.assertAlmostEqual(page2.current_parameters.get("temperature"), 0.5, places=2)
        self.assertEqual(page2.current_parameters.get("max_tokens"), 150)
        self.assertIn("OpenAI", page2.providers_data)
        self.assertTrue(page2.providers_data["OpenAI"]["connected"])
        self.assertEqual(page2.providers_data["OpenAI"]["api_key"], "key-123")


if __name__ == "__main__":
    unittest.main()
