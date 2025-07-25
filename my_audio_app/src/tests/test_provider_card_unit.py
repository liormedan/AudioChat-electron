"""
בדיקות יחידה לרכיב ProviderCard
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# הוספת נתיב
test_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(test_dir)
app_dir = os.path.dirname(src_dir)
sys.path.append(os.path.join(app_dir, 'src'))

from models.llm_models import LLMProvider, ProviderStatus
from services.llm_service import LLMService
from ui.components.llm.provider_card import ProviderCard
from datetime import datetime


class TestProviderCard(unittest.TestCase):
    """בדיקות יחידה לרכיב ProviderCard"""
    
    @classmethod
    def setUpClass(cls):
        """הגדרה כללית לכל הבדיקות"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לכל בדיקה"""
        # יצירת ספק לדוגמה
        self.provider = LLMProvider(
            name="OpenAI",
            api_base_url="https://api.openai.com/v1",
            supported_models=["gpt-4", "gpt-3.5-turbo"],
            connection_status=ProviderStatus.DISCONNECTED,
            is_connected=False,
            rate_limit=3500,
            cost_per_1k_tokens=0.03
        )
        
        # יצירת שירות מדומה
        self.mock_llm_service = Mock(spec=LLMService)
        self.mock_llm_service.get_provider.return_value = self.provider
        self.mock_llm_service.api_key_manager = Mock()
        
        # יצירת כרטיס
        self.card = ProviderCard(self.provider, self.mock_llm_service)
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        if hasattr(self, 'card'):
            self.card.close()
    
    def test_card_initialization(self):
        """בדיקת יצירת כרטיס"""
        self.assertIsNotNone(self.card)
        self.assertEqual(self.card.provider.name, "OpenAI")
        self.assertEqual(self.card.llm_service, self.mock_llm_service)
    
    def test_provider_icon(self):
        """בדיקת אייקון ספק"""
        icon = self.card.get_provider_icon()
        self.assertEqual(icon, "🤖")  # OpenAI icon
        
        # בדיקת ספק לא מוכר
        unknown_provider = LLMProvider(
            name="Unknown",
            api_base_url="https://example.com",
            supported_models=["model1"]
        )
        unknown_card = ProviderCard(unknown_provider, self.mock_llm_service)
        unknown_icon = unknown_card.get_provider_icon()
        self.assertEqual(unknown_icon, "🔧")  # Default icon
        unknown_card.close()
    
    def test_status_display_disconnected(self):
        """בדיקת תצוגת סטטוס מנותק"""
        self.card.update_status_display()
        status_text = self.card.status_label.text()
        self.assertEqual(status_text, "🔴 מנותק")
    
    def test_status_display_connected(self):
        """בדיקת תצוגת סטטוס מחובר"""
        self.provider.connection_status = ProviderStatus.CONNECTED
        self.provider.is_connected = True
        self.provider.last_test_date = datetime.now()
        
        self.card.update_status_display()
        status_text = self.card.status_label.text()
        self.assertEqual(status_text, "🟢 מחובר")
    
    def test_status_display_error(self):
        """בדיקת תצוגת סטטוס שגיאה"""
        self.provider.connection_status = ProviderStatus.ERROR
        self.provider.error_message = "Test error"
        
        self.card.update_status_display()
        status_text = self.card.status_label.text()
        self.assertEqual(status_text, "❌ שגיאה")
    
    def test_status_display_testing(self):
        """בדיקת תצוגת סטטוס בדיקה"""
        self.provider.connection_status = ProviderStatus.TESTING
        
        self.card.update_status_display()
        status_text = self.card.status_label.text()
        self.assertEqual(status_text, "🟡 בודק...")
    
    def test_primary_button_disconnected(self):
        """בדיקת כפתור ראשי במצב מנותק"""
        self.card.update_primary_button()
        button_text = self.card.primary_button.text()
        self.assertEqual(button_text, "🔗 חיבור")
    
    def test_primary_button_connected(self):
        """בדיקת כפתור ראשי במצב מחובר"""
        self.provider.connection_status = ProviderStatus.CONNECTED
        self.card.update_primary_button()
        button_text = self.card.primary_button.text()
        self.assertEqual(button_text, "⚙️ הגדרות")
    
    def test_models_display(self):
        """בדיקת תצוגת מודלים"""
        self.card.update_display()
        models_text = self.card.models_label.text()
        self.assertIn("gpt-4", models_text)
        self.assertIn("gpt-3.5-turbo", models_text)
    
    def test_cost_display(self):
        """בדיקת תצוגת עלות"""
        self.card.update_display()
        cost_text = self.card.cost_label.text()
        self.assertIn("$0.0300", cost_text)
        self.assertIn("1K tokens", cost_text)
    
    def test_rate_limit_display(self):
        """בדיקת תצוגת מגבלת קצב"""
        self.card.update_display()
        rate_text = self.card.rate_label.text()
        self.assertIn("3500", rate_text)
        self.assertIn("RPM", rate_text)
    
    def test_test_button_enabled_state(self):
        """בדיקת מצב כפתור בדיקה"""
        # במצב רגיל - מופעל
        self.card.update_display()
        self.assertTrue(self.card.test_button.isEnabled())
        
        # במצב בדיקה - מושבת
        self.provider.connection_status = ProviderStatus.TESTING
        self.card.update_display()
        self.assertFalse(self.card.test_button.isEnabled())
    
    def test_progress_show_hide(self):
        """בדיקת הצגה והסתרת פס התקדמות"""
        # הצגת פס התקדמות
        self.card.show_progress("Testing...")
        self.assertTrue(self.card.progress_bar.isVisible())
        self.assertTrue(self.card.status_message.isVisible())
        self.assertEqual(self.card.status_message.text(), "Testing...")
        self.assertFalse(self.card.primary_button.isEnabled())
        self.assertFalse(self.card.test_button.isEnabled())
        
        # הסתרת פס התקדמות
        self.card.hide_progress()
        self.assertFalse(self.card.progress_bar.isVisible())
        self.assertFalse(self.card.status_message.isVisible())
        self.assertTrue(self.card.primary_button.isEnabled())
        self.assertTrue(self.card.test_button.isEnabled())
    
    def test_provider_data_update(self):
        """בדיקת עדכון נתוני ספק"""
        # יצירת ספק מעודכן
        updated_provider = LLMProvider(
            name="OpenAI",
            api_base_url="https://api.openai.com/v1",
            supported_models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            connection_status=ProviderStatus.CONNECTED,
            is_connected=True,
            rate_limit=5000,
            cost_per_1k_tokens=0.025
        )
        
        # עדכון הכרטיס
        self.card.update_provider_data(updated_provider)
        
        # בדיקת העדכון
        self.assertEqual(self.card.provider.connection_status, ProviderStatus.CONNECTED)
        self.assertTrue(self.card.provider.is_connected)
        self.assertEqual(self.card.provider.rate_limit, 5000)
        self.assertEqual(self.card.provider.cost_per_1k_tokens, 0.025)
    
    @patch('src.ui.components.llm.provider_card.QMessageBox')
    def test_disconnect_provider_confirmation(self, mock_msgbox):
        """בדיקת אישור ניתוק ספק"""
        # הגדרת ספק מחובר
        self.provider.connection_status = ProviderStatus.CONNECTED
        self.provider.is_connected = True
        
        # הגדרת תגובת המשתמש - כן
        mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
        mock_msgbox.information = Mock()
        
        # ביצוע ניתוק
        self.card.disconnect_provider()
        
        # בדיקת קריאה לדיאלוג אישור
        mock_msgbox.question.assert_called_once()
        
        # בדיקת עדכון סטטוס
        self.assertEqual(self.provider.connection_status, ProviderStatus.DISCONNECTED)
        self.assertFalse(self.provider.is_connected)
    
    def test_signal_emission(self):
        """בדיקת שליחת אותות"""
        # יצירת mock לקבלת אותות
        connection_changed_mock = Mock()
        self.card.connection_changed.connect(connection_changed_mock)
        
        # הדמיית שינוי חיבור
        self.card.on_provider_connected("OpenAI")
        
        # בדיקה שהאות נשלח (בעקיפין דרך עדכון הספק)
        self.mock_llm_service.get_provider.assert_called_with("OpenAI")


class TestProviderCardIntegration(unittest.TestCase):
    """בדיקות אינטגרציה לרכיב ProviderCard"""
    
    @classmethod
    def setUpClass(cls):
        """הגדרה כללית לכל הבדיקות"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לכל בדיקה"""
        # יצירת שירות אמיתי (עם מסד נתונים זמני)
        self.llm_service = LLMService(":memory:")
        
        # יצירת ספק
        self.provider = LLMProvider(
            name="TestProvider",
            api_base_url="https://api.test.com/v1",
            supported_models=["test-model-1", "test-model-2"],
            connection_status=ProviderStatus.DISCONNECTED
        )
        
        # שמירת הספק בשירות
        self.llm_service.save_provider(self.provider)
        
        # יצירת כרטיס
        self.card = ProviderCard(self.provider, self.llm_service)
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        if hasattr(self, 'card'):
            self.card.close()
    
    def test_provider_refresh_integration(self):
        """בדיקת רענון נתוני ספק עם שירות אמיתי"""
        # עדכון הספק בשירות
        self.provider.rate_limit = 1000
        self.llm_service.save_provider(self.provider)
        
        # רענון הכרטיס
        self.card.refresh_provider_data()
        
        # בדיקת העדכון
        self.assertEqual(self.card.provider.rate_limit, 1000)


def run_tests():
    """הרצת כל הבדיקות"""
    # יצירת suite של בדיקות
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # הוספת בדיקות יחידה
    suite.addTests(loader.loadTestsFromTestCase(TestProviderCard))
    suite.addTests(loader.loadTestsFromTestCase(TestProviderCardIntegration))
    
    # הרצת הבדיקות
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)