"""
בדיקות יחידה לרכיב ModelSelector
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# הוספת נתיב לקבצי המקור
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from ui.components.llm.model_selector import ModelSelector, ModelListItem, ModelAvailabilityChecker
from models.llm_models import LLMModel, LLMProvider, ModelCapability
from services.llm_service import LLMService


class TestModelListItem(unittest.TestCase):
    """בדיקות לפריט מודל ברשימה"""
    
    @classmethod
    def setUpClass(cls):
        """הגדרה לכל הבדיקות"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לכל בדיקה"""
        self.test_model = LLMModel(
            id="test-model-1",
            name="Test Model",
            provider="TestProvider",
            description="A test model for unit testing",
            max_tokens=2048,
            cost_per_token=0.00002,
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
            is_active=False,
            is_available=True
        )
        
        self.model_item = ModelListItem(self.test_model)
    
    def test_model_item_creation(self):
        """בדיקת יצירת פריט מודל"""
        self.assertIsNotNone(self.model_item)
        self.assertEqual(self.model_item.model.id, "test-model-1")
        self.assertEqual(self.model_item.model.name, "Test Model")
    
    def test_model_item_display(self):
        """בדיקת תצוגת פריט מודל"""
        # בדיקת שם מודל
        self.assertEqual(self.model_item.name_label.text(), "Test Model")
        
        # בדיקת כפתורים
        self.assertTrue(self.model_item.select_button.isEnabled())
        self.assertTrue(self.model_item.activate_button.isEnabled())
    
    def test_active_model_display(self):
        """בדיקת תצוגת מודל פעיל"""
        # הגדרת מודל כפעיל
        active_model = LLMModel(
            id="active-model",
            name="Active Model",
            provider="TestProvider",
            description="Active test model",
            max_tokens=2048,
            cost_per_token=0.00002,
            capabilities=[ModelCapability.TEXT_GENERATION],
            is_active=True,
            is_available=True
        )
        
        active_item = ModelListItem(active_model)
        
        # בדיקת שכפתור ההפעלה מושבת
        self.assertFalse(active_item.activate_button.isEnabled())
    
    def test_availability_update(self):
        """בדיקת עדכון זמינות"""
        # בדיקת מודל זמין
        self.model_item.update_availability(True)
        self.assertTrue(self.model_item.select_button.isEnabled())
        self.assertTrue(self.model_item.activate_button.isEnabled())
        
        # בדיקת מודל לא זמין
        self.model_item.update_availability(False)
        self.assertFalse(self.model_item.select_button.isEnabled())
        self.assertFalse(self.model_item.activate_button.isEnabled())
    
    def test_model_selection_signal(self):
        """בדיקת אות בחירת מודל"""
        signal_received = False
        received_model_id = None
        
        def on_model_selected(model_id):
            nonlocal signal_received, received_model_id
            signal_received = True
            received_model_id = model_id
        
        self.model_item.model_selected.connect(on_model_selected)
        
        # לחיצה על כפתור בחירה
        QTest.mouseClick(self.model_item.select_button, Qt.MouseButton.LeftButton)
        
        self.assertTrue(signal_received)
        self.assertEqual(received_model_id, "test-model-1")
    
    def test_model_activation_signal(self):
        """בדיקת אות הפעלת מודל"""
        signal_received = False
        received_model_id = None
        
        def on_model_activated(model_id):
            nonlocal signal_received, received_model_id
            signal_received = True
            received_model_id = model_id
        
        self.model_item.model_activated.connect(on_model_activated)
        
        # לחיצה על כפתור הפעלה
        QTest.mouseClick(self.model_item.activate_button, Qt.MouseButton.LeftButton)
        
        self.assertTrue(signal_received)
        self.assertEqual(received_model_id, "test-model-1")
    
    def test_set_active_state(self):
        """בדיקת הגדרת מצב פעיל"""
        # הגדרה כפעיל
        self.model_item.set_active(True)
        self.assertTrue(self.model_item.model.is_active)
        self.assertFalse(self.model_item.activate_button.isEnabled())
        
        # הגדרה כלא פעיל
        self.model_item.set_active(False)
        self.assertFalse(self.model_item.model.is_active)
        self.assertTrue(self.model_item.activate_button.isEnabled())


class TestModelAvailabilityChecker(unittest.TestCase):
    """בדיקות לבודק זמינות מודלים"""
    
    @classmethod
    def setUpClass(cls):
        """הגדרה לכל הבדיקות"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לכל בדיקה"""
        self.mock_llm_service = Mock(spec=LLMService)
        self.model_ids = ["model-1", "model-2", "model-3"]
        
        self.checker = ModelAvailabilityChecker(self.mock_llm_service, self.model_ids)
    
    def test_checker_creation(self):
        """בדיקת יצירת בודק זמינות"""
        self.assertIsNotNone(self.checker)
        self.assertEqual(self.checker.model_ids, self.model_ids)
        self.assertTrue(self.checker.running)
    
    def test_checker_stop(self):
        """בדיקת עצירת בודק"""
        self.checker.stop()
        self.assertFalse(self.checker.running)


class TestModelSelector(unittest.TestCase):
    """בדיקות לרכיב בחירת מודלים"""
    
    @classmethod
    def setUpClass(cls):
        """הגדרה לכל הבדיקות"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לכל בדיקה"""
        # יצירת שירות LLM מדומה
        self.mock_llm_service = Mock(spec=LLMService)
        
        # נתוני בדיקה
        self.test_providers = [
            LLMProvider(
                name="TestProvider1",
                api_base_url="https://api.test1.com",
                supported_models=["model-1", "model-2"]
            ),
            LLMProvider(
                name="TestProvider2",
                api_base_url="https://api.test2.com",
                supported_models=["model-3"]
            )
        ]
        
        self.test_models = [
            LLMModel(
                id="model-1",
                name="Model 1",
                provider="TestProvider1",
                description="First test model",
                max_tokens=2048,
                cost_per_token=0.00002,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT]
            ),
            LLMModel(
                id="model-2",
                name="Model 2",
                provider="TestProvider1",
                description="Second test model",
                max_tokens=4096,
                cost_per_token=0.00003,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION]
            ),
            LLMModel(
                id="model-3",
                name="Model 3",
                provider="TestProvider2",
                description="Third test model",
                max_tokens=1024,
                cost_per_token=0.00001,
                capabilities=[ModelCapability.CHAT]
            )
        ]
        
        # הגדרת התנהגות השירות המדומה
        self.mock_llm_service.get_all_providers.return_value = self.test_providers
        self.mock_llm_service.get_all_models.return_value = self.test_models
        self.mock_llm_service.get_active_model.return_value = None
        self.mock_llm_service.set_active_model.return_value = True
        
        # יצירת רכיב
        self.model_selector = ModelSelector(self.mock_llm_service)
    
    def test_model_selector_creation(self):
        """בדיקת יצירת רכיב בחירת מודלים"""
        self.assertIsNotNone(self.model_selector)
        self.assertEqual(self.model_selector.llm_service, self.mock_llm_service)
    
    def test_load_models(self):
        """בדיקת טעינת מודלים"""
        # בדיקת שהמודלים נטענו
        self.assertEqual(len(self.model_selector.model_items), 3)
        
        # בדיקת שהספקים נטענו לפילטר
        provider_count = self.model_selector.provider_combo.count()
        self.assertGreaterEqual(provider_count, 3)  # "כל הספקים" + 2 ספקים
    
    def test_provider_filter(self):
        """בדיקת פילטר ספקים"""
        # בחירת ספק ספציפי
        self.model_selector.provider_combo.setCurrentText("TestProvider1")
        self.model_selector.filter_models()
        
        # בדיקת שרק מודלים של הספק הנבחר מוצגים
        visible_count = 0
        for model_item in self.model_selector.model_items.values():
            if model_item.isVisible():
                visible_count += 1
                self.assertEqual(model_item.model.provider, "TestProvider1")
        
        self.assertEqual(visible_count, 2)
    
    def test_search_filter(self):
        """בדיקת פילטר חיפוש"""
        # חיפוש מודל ספציפי
        self.model_selector.search_input.setText("Model 1")
        self.model_selector.filter_models()
        
        # בדיקת שרק המודל המתאים מוצג
        visible_count = 0
        for model_item in self.model_selector.model_items.values():
            if model_item.isVisible():
                visible_count += 1
                self.assertIn("Model 1", model_item.model.name)
        
        self.assertEqual(visible_count, 1)
    
    def test_capabilities_filter(self):
        """בדיקת פילטר יכולות"""
        # בחירת יכולת ספציפית
        self.model_selector.code_check.setChecked(True)
        self.model_selector.filter_models()
        
        # בדיקת שרק מודלים עם היכולת הנבחרת מוצגים
        visible_count = 0
        for model_item in self.model_selector.model_items.values():
            if model_item.isVisible():
                visible_count += 1
                self.assertIn(ModelCapability.CODE_GENERATION, model_item.model.capabilities)
        
        self.assertEqual(visible_count, 1)
    
    def test_model_selection_signal(self):
        """בדיקת אות בחירת מודל"""
        signal_received = False
        received_model_id = None
        
        def on_model_selected(model_id):
            nonlocal signal_received, received_model_id
            signal_received = True
            received_model_id = model_id
        
        self.model_selector.model_selected.connect(on_model_selected)
        
        # הדמיית בחירת מודל
        self.model_selector.on_model_item_selected("model-1")
        
        self.assertTrue(signal_received)
        self.assertEqual(received_model_id, "model-1")
    
    def test_model_activation(self):
        """בדיקת הפעלת מודל"""
        # הפעלת מודל
        self.model_selector.on_model_item_activated("model-1")
        
        # בדיקת שהשירות נקרא
        self.mock_llm_service.set_active_model.assert_called_once_with("model-1")
    
    def test_refresh_models(self):
        """בדיקת רענון מודלים"""
        # שינוי נתוני השירות
        new_model = LLMModel(
            id="model-4",
            name="Model 4",
            provider="TestProvider1",
            description="Fourth test model",
            max_tokens=8192,
            cost_per_token=0.00004,
            capabilities=[ModelCapability.TEXT_GENERATION]
        )
        
        self.mock_llm_service.get_all_models.return_value = self.test_models + [new_model]
        
        # רענון
        self.model_selector.refresh_models()
        
        # בדיקת שהמודל החדש נוסף
        self.assertEqual(len(self.model_selector.model_items), 4)
        self.assertIn("model-4", self.model_selector.model_items)
    
    def test_get_selected_model_id(self):
        """בדיקת קבלת ID מודל נבחר"""
        # הגדרת מודל פעיל
        active_model = self.test_models[0]
        active_model.is_active = True
        self.mock_llm_service.get_active_model.return_value = active_model
        
        # בדיקת קבלת ID
        selected_id = self.model_selector.get_selected_model_id()
        self.assertEqual(selected_id, "model-1")
    
    def test_combined_filters(self):
        """בדיקת שילוב פילטרים"""
        # הגדרת מספר פילטרים
        self.model_selector.provider_combo.setCurrentText("TestProvider1")
        self.model_selector.search_input.setText("Model")
        self.model_selector.text_gen_check.setChecked(True)
        
        self.model_selector.filter_models()
        
        # בדיקת שהפילטרים פועלים יחד
        visible_count = 0
        for model_item in self.model_selector.model_items.values():
            if model_item.isVisible():
                visible_count += 1
                self.assertEqual(model_item.model.provider, "TestProvider1")
                self.assertIn("Model", model_item.model.name)
                self.assertIn(ModelCapability.TEXT_GENERATION, model_item.model.capabilities)
        
        self.assertEqual(visible_count, 2)


if __name__ == '__main__':
    unittest.main()
