import unittest
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm_models import (
    LLMProvider, LLMModel, UsageRecord, LLMParameters,
    ProviderStatus, ModelCapability
)


class TestLLMProvider(unittest.TestCase):
    """בדיקות יחידה למודל LLMProvider"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        self.provider = LLMProvider(
            name="OpenAI",
            api_base_url="https://api.openai.com/v1",
            supported_models=["gpt-4", "gpt-3.5-turbo"],
            api_key="test-api-key-123",
            rate_limit=3500,
            cost_per_1k_tokens=0.03
        )
    
    def test_test_connection_with_api_key(self):
        """בדיקת חיבור עם API key"""
        result = self.provider.test_connection()
        
        self.assertTrue(result)
        self.assertEqual(self.provider.connection_status, ProviderStatus.CONNECTED)
        self.assertTrue(self.provider.is_connected)
        self.assertIsNotNone(self.provider.last_test_date)
        self.assertIsNone(self.provider.error_message)
    
    def test_test_connection_without_api_key(self):
        """בדיקת חיבור ללא API key"""
        self.provider.api_key = None
        result = self.provider.test_connection()
        
        self.assertFalse(result)
        self.assertEqual(self.provider.connection_status, ProviderStatus.ERROR)
        self.assertFalse(self.provider.is_connected)
        self.assertEqual(self.provider.error_message, "API key is required")
    
    def test_disconnect(self):
        """בדיקת ניתוק"""
        self.provider.test_connection()  # חיבור תחילה
        self.provider.disconnect()
        
        self.assertFalse(self.provider.is_connected)
        self.assertEqual(self.provider.connection_status, ProviderStatus.DISCONNECTED)
        self.assertIsNone(self.provider.error_message)
    
    def test_set_error(self):
        """בדיקת הגדרת שגיאה"""
        error_msg = "Connection timeout"
        self.provider.set_error(error_msg)
        
        self.assertEqual(self.provider.connection_status, ProviderStatus.ERROR)
        self.assertFalse(self.provider.is_connected)
        self.assertEqual(self.provider.error_message, error_msg)
    
    def test_status_display(self):
        """בדיקת תצוגת סטטוס"""
        # בדיקת סטטוסים שונים
        self.provider.connection_status = ProviderStatus.CONNECTED
        self.assertEqual(self.provider.status_display, "🟢 מחובר")
        
        self.provider.connection_status = ProviderStatus.DISCONNECTED
        self.assertEqual(self.provider.status_display, "🔴 מנותק")
        
        self.provider.connection_status = ProviderStatus.TESTING
        self.assertEqual(self.provider.status_display, "🟡 בודק חיבור")
        
        self.provider.connection_status = ProviderStatus.ERROR
        self.assertEqual(self.provider.status_display, "❌ שגיאה")
    
    def test_to_dict(self):
        """בדיקת המרה למילון"""
        provider_dict = self.provider.to_dict()
        
        self.assertEqual(provider_dict["name"], self.provider.name)
        self.assertEqual(provider_dict["api_base_url"], self.provider.api_base_url)
        self.assertEqual(provider_dict["supported_models"], self.provider.supported_models)
        self.assertEqual(provider_dict["api_key"], self.provider.api_key)
        self.assertEqual(provider_dict["connection_status"], self.provider.connection_status.value)
    
    def test_from_dict(self):
        """בדיקת יצירה ממילון"""
        provider_dict = self.provider.to_dict()
        new_provider = LLMProvider.from_dict(provider_dict)
        
        self.assertEqual(new_provider.name, self.provider.name)
        self.assertEqual(new_provider.api_base_url, self.provider.api_base_url)
        self.assertEqual(new_provider.supported_models, self.provider.supported_models)
        self.assertEqual(new_provider.connection_status, self.provider.connection_status)


class TestLLMModel(unittest.TestCase):
    """בדיקות יחידה למודל LLMModel"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        self.model = LLMModel(
            id="openai-gpt-4",
            name="GPT-4",
            provider="OpenAI",
            description="מודל שפה מתקדם",
            max_tokens=8192,
            cost_per_token=0.00003,
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
            context_window=8192
        )
    
    def test_display_name(self):
        """בדיקת שם תצוגה"""
        expected = "OpenAI - GPT-4"
        self.assertEqual(self.model.display_name, expected)
    
    def test_capabilities_display(self):
        """בדיקת תצוגת יכולות"""
        display = self.model.capabilities_display
        self.assertIn("יצירת טקסט", display)
        self.assertIn("שיחה", display)
    
    def test_cost_per_1k_tokens(self):
        """בדיקת עלות לאלף טוקנים"""
        expected = self.model.cost_per_token * 1000
        self.assertEqual(self.model.cost_per_1k_tokens, expected)
    
    def test_has_capability(self):
        """בדיקת יכולת"""
        self.assertTrue(self.model.has_capability(ModelCapability.TEXT_GENERATION))
        self.assertTrue(self.model.has_capability(ModelCapability.CHAT))
        self.assertFalse(self.model.has_capability(ModelCapability.CODE_GENERATION))
    
    def test_estimate_cost(self):
        """בדיקת הערכת עלות"""
        tokens = 1000
        expected_cost = tokens * self.model.cost_per_token
        self.assertEqual(self.model.estimate_cost(tokens), expected_cost)
    
    def test_to_dict(self):
        """בדיקת המרה למילון"""
        model_dict = self.model.to_dict()
        
        self.assertEqual(model_dict["id"], self.model.id)
        self.assertEqual(model_dict["name"], self.model.name)
        self.assertEqual(model_dict["provider"], self.model.provider)
        self.assertEqual(model_dict["capabilities"], [cap.value for cap in self.model.capabilities])
    
    def test_from_dict(self):
        """בדיקת יצירה ממילון"""
        model_dict = self.model.to_dict()
        new_model = LLMModel.from_dict(model_dict)
        
        self.assertEqual(new_model.id, self.model.id)
        self.assertEqual(new_model.name, self.model.name)
        self.assertEqual(new_model.capabilities, self.model.capabilities)


class TestUsageRecord(unittest.TestCase):
    """בדיקות יחידה למודל UsageRecord"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        self.usage_record = UsageRecord(
            id="usage-123",
            timestamp=datetime.now(),
            model_id="openai-gpt-4",
            provider="OpenAI",
            tokens_used=1500,
            cost=0.045,
            response_time=2.5,
            success=True
        )
    
    def test_cost_formatted(self):
        """בדיקת פורמט עלות"""
        # עלות קטנה
        small_cost_record = UsageRecord(**{**self.usage_record.to_dict(), "cost": 0.0025})
        small_cost_record.timestamp = datetime.now()
        self.assertEqual(small_cost_record.cost_formatted, "$0.0025")
        
        # עלות בינונית
        medium_cost_record = UsageRecord(**{**self.usage_record.to_dict(), "cost": 0.15})
        medium_cost_record.timestamp = datetime.now()
        self.assertEqual(medium_cost_record.cost_formatted, "$0.150")
        
        # עלות גדולה
        large_cost_record = UsageRecord(**{**self.usage_record.to_dict(), "cost": 1.25})
        large_cost_record.timestamp = datetime.now()
        self.assertEqual(large_cost_record.cost_formatted, "$1.25")
    
    def test_response_time_formatted(self):
        """בדיקת פורמט זמן תגובה"""
        # זמן קצר (מילישניות)
        fast_record = UsageRecord(**{**self.usage_record.to_dict(), "response_time": 0.5})
        fast_record.timestamp = datetime.now()
        self.assertEqual(fast_record.response_time_formatted, "500ms")
        
        # זמן ארוך (שניות)
        slow_record = UsageRecord(**{**self.usage_record.to_dict(), "response_time": 3.7})
        slow_record.timestamp = datetime.now()
        self.assertEqual(slow_record.response_time_formatted, "3.7s")
    
    def test_status_display(self):
        """בדיקת תצוגת סטטוס"""
        # הצלחה
        self.assertEqual(self.usage_record.status_display, "✅ הצליח")
        
        # כישלון
        failed_record = UsageRecord(**{**self.usage_record.to_dict(), "success": False})
        failed_record.timestamp = datetime.now()
        self.assertEqual(failed_record.status_display, "❌ נכשל")
    
    def test_to_dict(self):
        """בדיקת המרה למילון"""
        record_dict = self.usage_record.to_dict()
        
        self.assertEqual(record_dict["id"], self.usage_record.id)
        self.assertEqual(record_dict["model_id"], self.usage_record.model_id)
        self.assertEqual(record_dict["provider"], self.usage_record.provider)
        self.assertEqual(record_dict["tokens_used"], self.usage_record.tokens_used)
        self.assertEqual(record_dict["cost"], self.usage_record.cost)
        self.assertEqual(record_dict["success"], self.usage_record.success)
    
    def test_from_dict(self):
        """בדיקת יצירה ממילון"""
        record_dict = self.usage_record.to_dict()
        new_record = UsageRecord.from_dict(record_dict)
        
        self.assertEqual(new_record.id, self.usage_record.id)
        self.assertEqual(new_record.model_id, self.usage_record.model_id)
        self.assertEqual(new_record.tokens_used, self.usage_record.tokens_used)
        self.assertEqual(new_record.success, self.usage_record.success)


class TestLLMParameters(unittest.TestCase):
    """בדיקות יחידה למודל LLMParameters"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        self.params = LLMParameters(
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    
    def test_validate_valid_params(self):
        """בדיקת תקינות פרמטרים תקינים"""
        self.assertTrue(self.params.validate())
    
    def test_validate_invalid_temperature(self):
        """בדיקת פרמטר temperature לא תקין"""
        self.params.temperature = 3.0  # מעל 2.0
        self.assertFalse(self.params.validate())
        
        self.params.temperature = -0.5  # מתחת ל-0.0
        self.assertFalse(self.params.validate())
    
    def test_validate_invalid_top_p(self):
        """בדיקת פרמטר top_p לא תקין"""
        self.params.top_p = 1.5  # מעל 1.0
        self.assertFalse(self.params.validate())
        
        self.params.top_p = -0.1  # מתחת ל-0.0
        self.assertFalse(self.params.validate())
    
    def test_validate_invalid_max_tokens(self):
        """בדיקת פרמטר max_tokens לא תקין"""
        self.params.max_tokens = 0  # אפס או פחות
        self.assertFalse(self.params.validate())
        
        self.params.max_tokens = -100
        self.assertFalse(self.params.validate())
    
    def test_to_dict(self):
        """בדיקת המרה למילון"""
        params_dict = self.params.to_dict()
        
        self.assertEqual(params_dict["temperature"], self.params.temperature)
        self.assertEqual(params_dict["max_tokens"], self.params.max_tokens)
        self.assertEqual(params_dict["top_p"], self.params.top_p)
        self.assertEqual(params_dict["frequency_penalty"], self.params.frequency_penalty)
        self.assertEqual(params_dict["presence_penalty"], self.params.presence_penalty)
    
    def test_from_dict(self):
        """בדיקת יצירה ממילון"""
        params_dict = self.params.to_dict()
        new_params = LLMParameters.from_dict(params_dict)
        
        self.assertEqual(new_params.temperature, self.params.temperature)
        self.assertEqual(new_params.max_tokens, self.params.max_tokens)
        self.assertEqual(new_params.top_p, self.params.top_p)
    
    def test_get_preset_creative(self):
        """בדיקת פרסט יצירתי"""
        creative = LLMParameters.get_preset("creative")
        
        self.assertEqual(creative.temperature, 0.9)
        self.assertEqual(creative.max_tokens, 1500)
        self.assertEqual(creative.frequency_penalty, 0.3)
    
    def test_get_preset_balanced(self):
        """בדיקת פרסט מאוזן"""
        balanced = LLMParameters.get_preset("balanced")
        
        self.assertEqual(balanced.temperature, 0.7)
        self.assertEqual(balanced.max_tokens, 1000)
        self.assertEqual(balanced.frequency_penalty, 0.0)
    
    def test_get_preset_precise(self):
        """בדיקת פרסט מדויק"""
        precise = LLMParameters.get_preset("precise")
        
        self.assertEqual(precise.temperature, 0.3)
        self.assertEqual(precise.max_tokens, 800)
        self.assertEqual(precise.frequency_penalty, 0.0)
    
    def test_get_preset_unknown(self):
        """בדיקת פרסט לא ידוע"""
        unknown = LLMParameters.get_preset("unknown_preset")
        
        # אמור להחזיר פרמטרים ברירת מחדל
        self.assertEqual(unknown.temperature, 0.7)
        self.assertEqual(unknown.max_tokens, 1000)


if __name__ == "__main__":
    unittest.main()
