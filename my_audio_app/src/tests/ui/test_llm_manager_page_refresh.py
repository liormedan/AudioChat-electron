import sys
import os
import unittest
from unittest.mock import Mock

from PyQt6.QtWidgets import QApplication, QWidget, QLabel

# Add project src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ui.pages.llm_manager_page import LLMManagerPage


class DummyCard:
    def __init__(self):
        self.value = None

    def update_value(self, value, change=None):
        self.value = value


class DummyUsageMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.tokens_card = DummyCard()
        self.calls_card = DummyCard()
        self.cost_card = DummyCard()
        self.errors_card = DummyCard()
        self.avg_response_time_label = QLabel()
        self.success_rate_label = QLabel()
        self.active_providers_label = QLabel()
        self.active_models_label = QLabel()


class DummyTester(QWidget):
    def __init__(self):
        super().__init__()
        self.history_called = False
        self.metrics_called = False

    def update_history_table(self):
        self.history_called = True

    def update_performance_metrics(self):
        self.metrics_called = True


class TestLLMManagerPageRefresh(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.page = LLMManagerPage()

        # Replace services and widgets with dummies
        self.mock_service = Mock()
        self.page.usage_service = self.mock_service

        self.dummy_usage = DummyUsageMonitor()
        self.page.usage_monitor = self.dummy_usage

        self.dummy_tester = DummyTester()
        self.page.model_tester = self.dummy_tester

    def test_refresh_usage_data_updates_monitor(self):
        summary = {
            "total_requests": 10,
            "total_tokens": 5000,
            "total_cost": 1.5,
            "avg_response_time": 2.0,
            "success_rate": 0.8,
            "unique_providers": 2,
            "unique_models": 3,
        }
        self.mock_service.get_usage_summary.return_value = summary

        self.page._refresh_usage_data()

        self.assertEqual(self.dummy_usage.tokens_card.value, "5,000")
        self.assertEqual(self.dummy_usage.calls_card.value, "10")
        self.assertEqual(self.dummy_usage.cost_card.value, "$1.50")
        self.assertEqual(self.dummy_usage.errors_card.value, "2")
        self.assertEqual(self.dummy_usage.avg_response_time_label.text(), "2.00s")
        self.assertEqual(self.dummy_usage.success_rate_label.text(), "80.0%")
        self.assertEqual(self.dummy_usage.active_providers_label.text(), "2")
        self.assertEqual(self.dummy_usage.active_models_label.text(), "3")

    def test_refresh_testing_data_calls_update_methods(self):
        self.page._refresh_testing_data()
        self.assertTrue(self.dummy_tester.history_called)
        self.assertTrue(self.dummy_tester.metrics_called)


if __name__ == "__main__":
    unittest.main()

