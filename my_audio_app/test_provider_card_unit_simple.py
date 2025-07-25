"""
בדיקות יחידה פשוטות לרכיב ProviderCard
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication

# הוספת נתיב
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.llm_models import LLMProvider, ProviderStatus
from services.llm_service import LLMService
from ui.components.llm.provider_card import ProviderCard
from datetime import datetime


class TestProviderCardBasic(unittest.TestCase):
    """בדיקות בסיסיות לרכיב ProviderCard"""
    
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
    
    def test_card_creation(self):
        """בדיקת יצירת כרטיס"""
        self.assertIsNotNone(self.card)
        self.assertEqual(self.card.provider.name, "OpenAI")
        print("✅ Card creation test passed")
    
    def test_provider_icon(self):
        """בדיקת אייקון ספק"""
        icon = self.card.get_provider_icon()
        self.assertEqual(icon, "🤖")  # OpenAI icon
        print("✅ Provider icon test passed")
    
    def test_status_display(self):
        """בדיקת תצוגת סטטוס"""
        self.card.update_status_display()
        status_text = self.card.status_label.text()
        self.assertEqual(status_text, "🔴 מנותק")
        print("✅ Status display test passed")
    
    def test_primary_button_text(self):
        """בדיקת טקסט כפתור ראשי"""
        self.card.update_primary_button()
        button_text = self.card.primary_button.text()
        self.assertEqual(button_text, "🔗 חיבור")
        print("✅ Primary button text test passed")
    
    def test_models_display(self):
        """בדיקת תצוגת מודלים"""
        self.card.update_display()
        models_text = self.card.models_label.text()
        self.assertIn("gpt-4", models_text)
        self.assertIn("gpt-3.5-turbo", models_text)
        print("✅ Models display test passed")
    
    def test_cost_and_rate_display(self):
        """בדיקת תצוגת עלות ומגבלת קצב"""
        self.card.update_display()
        
        cost_text = self.card.cost_label.text()
        self.assertIn("$0.0300", cost_text)
        
        rate_text = self.card.rate_label.text()
        self.assertIn("3500", rate_text)
        print("✅ Cost and rate display test passed")
    
    def test_progress_functionality(self):
        """בדיקת פונקציונליות פס התקדמות"""
        # בדיקת מצב התחלתי
        self.assertFalse(self.card.progress_bar.isVisible())
        self.assertFalse(self.card.status_message.isVisible())
        
        # הצגת פס התקדמות
        self.card.show_progress("Testing...")
        
        # בדיקת הודעת סטטוס (זה אמור לעבוד)
        self.assertEqual(self.card.status_message.text(), "Testing...")
        
        # בדיקת השבתת כפתורים
        self.assertFalse(self.card.primary_button.isEnabled())
        self.assertFalse(self.card.test_button.isEnabled())
        
        # הסתרת פס התקדמות
        self.card.hide_progress()
        
        # בדיקת הפעלת כפתורים
        self.assertTrue(self.card.primary_button.isEnabled())
        self.assertTrue(self.card.test_button.isEnabled())
        
        print("✅ Progress functionality test passed")
    
    def test_provider_data_update(self):
        """בדיקת עדכון נתוני ספק"""
        # יצירת ספק מעודכן
        updated_provider = LLMProvider(
            name="OpenAI",
            api_base_url="https://api.openai.com/v1",
            supported_models=["gpt-4", "gpt-4-turbo"],
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
        print("✅ Provider data update test passed")
    
    def test_different_provider_icons(self):
        """בדיקת אייקונים לספקים שונים"""
        providers_icons = {
            "OpenAI": "🤖",
            "Anthropic": "🧠",
            "Google": "🔍",
            "Cohere": "💬",
            "Hugging Face": "🤗",
            "Unknown": "🔧"
        }
        
        for provider_name, expected_icon in providers_icons.items():
            test_provider = LLMProvider(
                name=provider_name,
                api_base_url="https://example.com",
                supported_models=["test-model"]
            )
            test_card = ProviderCard(test_provider, self.mock_llm_service)
            actual_icon = test_card.get_provider_icon()
            self.assertEqual(actual_icon, expected_icon)
            test_card.close()
        
        print("✅ Different provider icons test passed")
    
    def test_status_changes(self):
        """בדיקת שינויי סטטוס"""
        status_tests = [
            (ProviderStatus.CONNECTED, "🟢 מחובר"),
            (ProviderStatus.DISCONNECTED, "🔴 מנותק"),
            (ProviderStatus.TESTING, "🟡 בודק..."),
            (ProviderStatus.ERROR, "❌ שגיאה")
        ]
        
        for status, expected_text in status_tests:
            self.provider.connection_status = status
            self.card.update_status_display()
            actual_text = self.card.status_label.text()
            self.assertEqual(actual_text, expected_text)
        
        print("✅ Status changes test passed")


def run_basic_tests():
    """הרצת בדיקות בסיסיות"""
    print("🧪 Running Provider Card Basic Tests...")
    print("=" * 50)
    
    # יצירת suite של בדיקות
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestProviderCardBasic)
    
    # הרצת הבדיקות
    runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
        print(f"✅ Ran {result.testsRun} tests")
    else:
        print("❌ Some tests failed:")
        for failure in result.failures:
            print(f"  - {failure[0]}: {failure[1]}")
        for error in result.errors:
            print(f"  - {error[0]}: {error[1]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_basic_tests()
    
    if success:
        print("\n🚀 Provider Card component is working correctly!")
        print("Key features tested:")
        print("  ✅ Card creation and initialization")
        print("  ✅ Provider icons for different providers")
        print("  ✅ Status display for all connection states")
        print("  ✅ Primary button text updates")
        print("  ✅ Models and cost information display")
        print("  ✅ Progress bar functionality")
        print("  ✅ Provider data updates")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    sys.exit(0 if success else 1)