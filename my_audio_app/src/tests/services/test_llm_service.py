import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import LLMService
from models.llm_models import (
    LLMProvider, LLMModel, LLMParameters,
    ProviderStatus, ModelCapability
)


class TestLLMService(unittest.TestCase):
    """בדיקות יחידה לשירות LLM"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        # יצירת קובץ מסד נתונים זמני
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # יצירת שירות עם מסד נתונים זמני
        self.llm_service = LLMService(db_path=self.temp_db.name)
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        # מחיקת קובץ מסד הנתונים הזמני
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_init_creates_default_providers(self):
        """בדיקה שהשירות יוצר ספקים ברירת מחדל"""
        providers = self.llm_service.get_all_providers()
        
        # בדיקה שיש לפחות כמה ספקים ברירת מחדל
        self.assertGreater(len(providers), 0)
        
        # בדיקה שיש ספקים מוכרים
        provider_names = [p.name for p in providers]
        self.assertIn("OpenAI", provider_names)
        self.assertIn("Anthropic", provider_names)
        self.assertIn("Google", provider_names)
    
    def test_init_creates_default_models(self):
        """בדיקה שהשירות יוצר מודלים ברירת מחדל"""
        models = self.llm_service.get_all_models()
        
        # בדיקה שיש לפחות כמה מודלים ברירת מחדל
        self.assertGreater(len(models), 0)
        
        # בדיקה שיש מודלים מוכרים
        model_ids = [m.id for m in models]
        self.assertIn("openai-gpt-4", model_ids)
        self.assertIn("openai-gpt-3.5-turbo", model_ids)
    
    def test_save_and_get_provider(self):
        """בדיקת שמירה וקבלת ספק"""
        # יצירת ספק חדש
        provider = LLMProvider(
            name="TestProvider",
            api_base_url="https://api.test.com",
            supported_models=["test-model-1", "test-model-2"],
            api_key="test-key-123",
            rate_limit=1000,
            cost_per_1k_tokens=0.01
        )
        
        # שמירת הספק
        self.llm_service.save_provider(provider)
        
        # קבלת הספק
        retrieved_provider = self.llm_service.get_provider("TestProvider")
        
        # בדיקות
        self.assertIsNotNone(retrieved_provider)
        self.assertEqual(retrieved_provider.name, provider.name)
        self.assertEqual(retrieved_provider.api_base_url, provider.api_base_url)
        self.assertEqual(retrieved_provider.supported_models, provider.supported_models)
        self.assertEqual(retrieved_provider.api_key, provider.api_key)
        self.assertEqual(retrieved_provider.rate_limit, provider.rate_limit)
    
    def test_get_nonexistent_provider(self):
        """בדיקת קבלת ספק שלא קיים"""
        provider = self.llm_service.get_provider("NonExistentProvider")
        self.assertIsNone(provider)
    
    @patch.object(LLMProvider, 'test_connection')
    def test_test_provider_connection_success(self, mock_test_connection):
        """בדיקת בדיקת חיבור מוצלחת לספק"""
        # הגדרת mock להחזיר True
        mock_test_connection.return_value = True
        
        # יצירת ספק
        provider = LLMProvider(
            name="TestProvider",
            api_base_url="https://api.test.com",
            supported_models=["test-model"],
            api_key="test-key"
        )
        self.llm_service.save_provider(provider)
        
        # בדיקת חיבור
        result = self.llm_service.test_provider_connection("TestProvider")
        
        # בדיקות
        self.assertTrue(result)
        mock_test_connection.assert_called_once()
    
    @patch.object(LLMProvider, 'test_connection')
    def test_test_provider_connection_failure(self, mock_test_connection):
        """בדיקת בדיקת חיבור כושלת לספק"""
        # הגדרת mock להחזיר False
        mock_test_connection.return_value = False
        
        # יצירת ספק
        provider = LLMProvider(
            name="TestProvider",
            api_base_url="https://api.test.com",
            supported_models=["test-model"]
        )
        self.llm_service.save_provider(provider)
        
        # בדיקת חיבור
        result = self.llm_service.test_provider_connection("TestProvider")
        
        # בדיקות
        self.assertFalse(result)
        mock_test_connection.assert_called_once()
    
    def test_save_and_get_model(self):
        """בדיקת שמירה וקבלת מודל"""
        # יצירת מודל חדש
        model = LLMModel(
            id="test-model-123",
            name="Test Model",
            provider="TestProvider",
            description="מודל לבדיקה",
            max_tokens=2048,
            cost_per_token=0.00001,
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
            context_window=4096
        )
        
        # שמירת המודל
        self.llm_service.save_model(model)
        
        # קבלת המודל
        retrieved_model = self.llm_service.get_model("test-model-123")
        
        # בדיקות
        self.assertIsNotNone(retrieved_model)
        self.assertEqual(retrieved_model.id, model.id)
        self.assertEqual(retrieved_model.name, model.name)
        self.assertEqual(retrieved_model.provider, model.provider)
        self.assertEqual(retrieved_model.capabilities, model.capabilities)
    
    def test_get_models_by_provider(self):
        """בדיקת קבלת מודלים לפי ספק"""
        # יצירת מודלים לספק מסוים
        model1 = LLMModel(
            id="test-model-1",
            name="Test Model 1",
            provider="TestProvider",
            description="מודל ראשון",
            max_tokens=1024,
            cost_per_token=0.00001,
            capabilities=[ModelCapability.TEXT_GENERATION]
        )
        
        model2 = LLMModel(
            id="test-model-2",
            name="Test Model 2",
            provider="TestProvider",
            description="מודל שני",
            max_tokens=2048,
            cost_per_token=0.00002,
            capabilities=[ModelCapability.CHAT]
        )
        
        # מודל לספק אחר
        model3 = LLMModel(
            id="other-model",
            name="Other Model",
            provider="OtherProvider",
            description="מודל אחר",
            max_tokens=1024,
            cost_per_token=0.00001,
            capabilities=[ModelCapability.TEXT_GENERATION]
        )
        
        # שמירת המודלים
        self.llm_service.save_model(model1)
        self.llm_service.save_model(model2)
        self.llm_service.save_model(model3)
        
        # קבלת מודלים לפי ספק
        test_provider_models = self.llm_service.get_models_by_provider("TestProvider")
        
        # בדיקות
        self.assertEqual(len(test_provider_models), 2)
        model_ids = [m.id for m in test_provider_models]
        self.assertIn("test-model-1", model_ids)
        self.assertIn("test-model-2", model_ids)
        self.assertNotIn("other-model", model_ids)
    
    def test_set_and_get_active_model(self):
        """בדיקת הגדרה וקבלת מודל פעיל"""
        # יצירת מודל
        model = LLMModel(
            id="active-test-model",
            name="Active Test Model",
            provider="TestProvider",
            description="מודל פעיל לבדיקה",
            max_tokens=1024,
            cost_per_token=0.00001,
            capabilities=[ModelCapability.TEXT_GENERATION]
        )
        
        # שמירת המודל
        self.llm_service.save_model(model)
        
        # הגדרת המודל כפעיל
        result = self.llm_service.set_active_model("active-test-model")
        self.assertTrue(result)
        
        # קבלת המודל הפעיל
        active_model = self.llm_service.get_active_model()
        
        # בדיקות
        self.assertIsNotNone(active_model)
        self.assertEqual(active_model.id, "active-test-model")
        self.assertTrue(active_model.is_active)
    
    def test_set_active_model_nonexistent(self):
        """בדיקת הגדרת מודל פעיל שלא קיים"""
        result = self.llm_service.set_active_model("nonexistent-model")
        self.assertFalse(result)
    
    def test_set_and_get_parameters(self):
        """בדיקת הגדרה וקבלת פרמטרים"""
        # יצירת פרמטרים
        params = LLMParameters(
            temperature=0.8,
            max_tokens=1500,
            top_p=0.95,
            frequency_penalty=0.1,
            presence_penalty=0.05
        )
        
        # הגדרת הפרמטרים
        result = self.llm_service.set_parameters(params)
        self.assertTrue(result)
        
        # קבלת הפרמטרים
        retrieved_params = self.llm_service.get_parameters()
        
        # בדיקות
        self.assertEqual(retrieved_params.temperature, params.temperature)
        self.assertEqual(retrieved_params.max_tokens, params.max_tokens)
        self.assertEqual(retrieved_params.top_p, params.top_p)
        self.assertEqual(retrieved_params.frequency_penalty, params.frequency_penalty)
        self.assertEqual(retrieved_params.presence_penalty, params.presence_penalty)
    
    def test_set_invalid_parameters(self):
        """בדיקת הגדרת פרמטרים לא תקינים"""
        # יצירת פרמטרים לא תקינים
        invalid_params = LLMParameters(
            temperature=3.0,  # מעל 2.0
            max_tokens=1000,
            top_p=0.9
        )
        
        # ניסיון הגדרת הפרמטרים
        result = self.llm_service.set_parameters(invalid_params)
        self.assertFalse(result)
    
    def test_signals_emitted(self):
        """בדיקת שליחת אותות"""
        # רישום לאותות
        provider_connected_signal = MagicMock()
        model_activated_signal = MagicMock()
        
        self.llm_service.provider_connected.connect(provider_connected_signal)
        self.llm_service.model_activated.connect(model_activated_signal)
        
        # יצירת ספק ומודל
        provider = LLMProvider(
            name="SignalTestProvider",
            api_base_url="https://api.test.com",
            supported_models=["test-model"],
            api_key="test-key"
        )
        
        model = LLMModel(
            id="signal-test-model",
            name="Signal Test Model",
            provider="SignalTestProvider",
            description="מודל לבדיקת אותות",
            max_tokens=1024,
            cost_per_token=0.00001,
            capabilities=[ModelCapability.TEXT_GENERATION]
        )
        
        # שמירת ספק ומודל
        self.llm_service.save_provider(provider)
        self.llm_service.save_model(model)
        
        # בדיקת חיבור (אמור לשלוח אות)
        with patch.object(provider, 'test_connection', return_value=True):
            self.llm_service.test_provider_connection("SignalTestProvider")
        
        # הגדרת מודל פעיל (אמור לשלוח אות)
        self.llm_service.set_active_model("signal-test-model")
        
        # בדיקת שליחת אותות
        provider_connected_signal.assert_called_once_with("SignalTestProvider")
        model_activated_signal.assert_called_once_with("signal-test-model")


if __name__ == "__main__":
    unittest.main()
