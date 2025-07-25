import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication

from ui.pages.llm_manager_page import LLMManagerPage

class TestLLMManagerPageConnectProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.patcher = patch('ui.pages.llm_manager_page.llm_service')
        self.mock_service = self.patcher.start()
        self.mock_service.get_all_providers.return_value = []
        self.mock_service.get_active_model.return_value = None
        self.mock_service.set_provider_api_key.return_value = True
        self.mock_service.test_provider_connection_secure.return_value = (True, 'ok', 0.1)
        self.page = LLMManagerPage()

    def tearDown(self):
        self.page.close()
        self.patcher.stop()

    def test_connect_provider_success(self):
        signals = []
        self.page.provider_connected.connect(lambda n, c: signals.append((n, c)))

        result = self.page.connect_provider('OpenAI', 'key')

        self.assertTrue(result)
        self.mock_service.set_provider_api_key.assert_called_with('OpenAI', 'key')
        self.mock_service.test_provider_connection_secure.assert_called_with('OpenAI')
        self.assertIn('OpenAI', self.page.providers_data)
        self.assertTrue(self.page.providers_data['OpenAI']['connected'])
        self.assertEqual(signals, [('OpenAI', True)])

    def test_connect_provider_failure(self):
        self.mock_service.test_provider_connection_secure.return_value = (False, 'err', 0.2)
        signals = []
        self.page.provider_connected.connect(lambda n, c: signals.append((n, c)))

        result = self.page.connect_provider('OpenAI', 'key')

        self.assertFalse(result)
        self.mock_service.set_provider_api_key.assert_called_with('OpenAI', 'key')
        self.mock_service.test_provider_connection_secure.assert_called_with('OpenAI')
        self.assertIn('OpenAI', self.page.providers_data)
        self.assertFalse(self.page.providers_data['OpenAI']['connected'])
        self.assertEqual(signals, [('OpenAI', False)])

if __name__ == '__main__':
    unittest.main()
