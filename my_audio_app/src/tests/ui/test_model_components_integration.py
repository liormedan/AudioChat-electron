"""
בדיקות אינטגרציה לרכיבי מודל LLM
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# הוספת נתיב לקבצי המקור
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from ui.components.llm.model_selector import ModelSelector
from ui.components.llm.model_details import ModelDetailsWidget
from models.llm_models import LLMModel, LLMProvider, ModelCapability
from services.llm_service import LLMService


class TestModelComponentsIntegration(unittest.TestCase):
    """בדיקות אינטגרציה בין רכיבי מודל"""
    
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
                description="First test model for integration testing",
                max_tokens=2048,
                cost_per_token=0.00002,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
                is_active=False,
                is_available=True,
                version="1.0"
            ),
            LLMModel(
                id="model-2",
                name="Model 2",
                provider="TestProvider1",
                description="Second test model for integration testing",
                max_tokens=4096,
                cost_per_token=0.00003,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                is_active=False,
                is_available=True,
                version="2.0"
            ),
            LLMModel(
                id="model-3",
                name="Model 3",
                provider="TestProvider2",
                description="Third test model for integration testing",
                max_tokens=1024,
                cost_per_token=0.00001,
                capabilities=[ModelCapability.CHAT],
                is_active=True,
                is_available=True,
                version="1.5"
            )
        ]
        
        # הגדרת התנהגות השירות המדומה
        self.mock_llm_service.get_all_providers.return_value = self.test_providers
        self.mock_llm_service.get_all_models.return_value = self.test_models
        self.mock_llm_service.get_active_model.return_value = self.test_models[2]  # model-3 פעיל
        self.mock_llm_service.set_active_model.return_value = True
        
        # מפה של מודלים לפי ID
        self.models_by_id = {model.id: model for model in self.test_models}
        self.mock_llm_service.get_model.side_effect = lambda model_id: self.models_by_id.get(model_id)
        self.mock_llm_service.get_models_by_provider.side_effect = lambda provider: [
            model for model in self.test_models if model.provider == provider
        ]
        
        # יצירת רכיבים
        self.model_selector = ModelSelector(self.mock_llm_service)
        self.model_details = ModelDetailsWidget(self.mock_llm_service)
        
        # חיבור אותות
        self.model_selector.model_selected.connect(self.model_details.show_model_details)
        self.model_selector.model_activated.connect(self.on_model_activated)
        self.model_details.model_activated.connect(self.on_model_activated)
        
        # משתנה למעקב אחר הפעלות
        self.activated_models = []
    
    def on_model_activated(self, model_id: str):
        """טיפול בהפעלת מודל"""
        self.activated_models.append(model_id)
        
        # עדכון מצב המודלים
        for model in self.test_models:
            model.is_active = (model.id == model_id)
        
        # עדכון השירות המדומה
        active_model = self.models_by_id.get(model_id)
        self.mock_llm_service.get_active_model.return_value = active_model
    
    def test_components_creation(self):
        """בדיקת יצירת רכיבים"""
        self.assertIsNotNone(self.model_selector)
        self.assertIsNotNone(self.model_details)
        
        # בדיקת שהרכיבים מחוברים לאותו שירות
        self.assertEqual(self.model_selector.llm_service, self.mock_llm_service)
        self.assertEqual(self.model_details.llm_service, self.mock_llm_service)
    
    def test_model_selection_updates_details(self):
        """בדיקת שבחירת מודל מעדכנת את הפרטים"""
        # בחירת מודל
        self.model_selector.on_model_item_selected("model-1")
        
        # בדיקת שהפרטים עודכנו
        self.assertEqual(self.model_details.current_model.id, "model-1")
        self.assertEqual(self.model_details.name_value.text(), "Model 1")
        self.assertEqual(self.model_details.provider_value.text(), "TestProvider1")
    
    def test_model_activation_from_selector(self):
        """בדיקת הפעלת מודל מהבוחר"""
        # הפעלת מודל מהבוחר
        self.model_selector.on_model_item_activated("model-1")
        
        # בדיקת שהמודל הופעל
        self.assertIn("model-1", self.activated_models)
        self.mock_llm_service.set_active_model.assert_called_with("model-1")
    
    def test_model_activation_from_details(self):
        """בדיקת הפעלת מודל מהפרטים"""
        # בחירת מודל ראשית
        self.model_details.show_model_details("model-2")
        
        # הפעלת מודל מהפרטים
        self.model_details.activate_model()
        
        # בדיקת שהמודל הופעל
        self.assertIn("model-2", self.activated_models)
        self.mock_llm_service.set_active_model.assert_called_with("model-2")
    
    def test_active_model_indicator_sync(self):
        """בדיקת סנכרון אינדיקטור מודל פעיל"""
        # הפעלת מודל
        self.on_model_activated("model-1")
        
        # בדיקת שהמודל מסומן כפעיל ברכיבים
        if "model-1" in self.model_selector.model_items:
            model_item = self.model_selector.model_items["model-1"]
            self.assertTrue(model_item.model.is_active)
        
        # בדיקת שהפרטים מציגים מודל פעיל
        self.model_details.show_model_details("model-1")
        self.assertFalse(self.model_details.activate_button.isEnabled())
    
    def test_provider_filtering_affects_details(self):
        """בדיקת שפילטור ספקים משפיע על הפרטים"""
        # פילטור לספק ספציפי
        self.model_selector.provider_combo.setCurrentText("TestProvider1")
        self.model_selector.filter_models()
        
        # בדיקת שרק מודלים של הספק הנבחר מוצגים
        visible_models = []
        for model_id, model_item in self.model_selector.model_items.items():
            if model_item.isVisible():
                visible_models.append(model_id)
        
        # בדיקת שכל המודלים הגלויים שייכים לספק הנכון
        for model_id in visible_models:
            model = self.models_by_id[model_id]
            self.assertEqual(model.provider, "TestProvider1")
    
    def test_model_comparison_integration(self):
        """בדיקת אינטגרציה של השוואת מודלים"""
        # בחירת מודל
        self.model_details.show_model_details("model-1")
        
        # בדיקת שכפתור השוואה זמין
        self.assertTrue(self.model_details.compare_button.isEnabled())
        
        # הדמיית השוואה
        with patch('ui.components.llm.model_details.ModelComparisonDialog') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog.return_value = mock_dialog_instance
            
            self.model_details.show_comparison()
            
            # בדיקת שהדיאלוג נוצר עם המודלים הנכונים
            mock_dialog.assert_called_once()
            call_args = mock_dialog.call_args[0][0]  # רשימת המודלים
            
            # בדיקת שהמודל הנוכחי כלול
            model_ids = [model.id for model in call_args]
            self.assertIn("model-1", model_ids)
    
    def test_availability_check_integration(self):
        """בדיקת אינטגרציה של בדיקת זמינות"""
        # הדמיית עדכון זמינות
        self.model_selector.on_availability_checked("model-1", True)
        
        # בדיקת שהמודל מסומן כזמין
        if "model-1" in self.model_selector.model_items:
            model_item = self.model_selector.model_items["model-1"]
            self.assertTrue(model_item.select_button.isEnabled())
            self.assertTrue(model_item.activate_button.isEnabled())
        
        # הדמיית מודל לא זמין
        self.model_selector.on_availability_checked("model-2", False)
        
        # בדיקת שהמודל מסומן כלא זמין
        if "model-2" in self.model_selector.model_items:
            model_item = self.model_selector.model_items["model-2"]
            self.assertFalse(model_item.select_button.isEnabled())
            self.assertFalse(model_item.activate_button.isEnabled())
    
    def test_search_and_selection_integration(self):
        """בדיקת אינטגרציה של חיפוש ובחירה"""
        # חיפוש מודל ספציפי
        self.model_selector.search_input.setText("Model 2")
        self.model_selector.filter_models()
        
        # בדיקת שרק המודל המתאים מוצג
        visible_count = 0
        visible_model_id = None
        
        for model_id, model_item in self.model_selector.model_items.items():
            if model_item.isVisible():
                visible_count += 1
                visible_model_id = model_id
        
        self.assertEqual(visible_count, 1)
        self.assertEqual(visible_model_id, "model-2")
        
        # בחירת המודל הגלוי
        if visible_model_id:
            self.model_selector.on_model_item_selected(visible_model_id)
            
            # בדיקת שהפרטים עודכנו
            self.assertEqual(self.model_details.current_model.id, visible_model_id)
    
    def test_capabilities_filter_integration(self):
        """בדיקת אינטגרציה של פילטר יכולות"""
        # פילטור לפי יכולת קוד
        self.model_selector.code_check.setChecked(True)
        self.model_selector.filter_models()
        
        # בדיקת שרק מודלים עם יכולת קוד מוצגים
        visible_models = []
        for model_id, model_item in self.model_selector.model_items.items():
            if model_item.isVisible():
                visible_models.append(model_id)
                model = self.models_by_id[model_id]
                self.assertIn(ModelCapability.CODE_GENERATION, model.capabilities)
        
        # בדיקת שיש לפחות מודל אחד עם יכולת קוד
        self.assertGreater(len(visible_models), 0)
    
    def test_refresh_synchronization(self):
        """בדיקת סנכרון רענון"""
        # הוספת מודל חדש
        new_model = LLMModel(
            id="model-4",
            name="Model 4",
            provider="TestProvider1",
            description="New test model",
            max_tokens=8192,
            cost_per_token=0.00004,
            capabilities=[ModelCapability.TEXT_GENERATION],
            is_active=False,
            is_available=True
        )
        
        # עדכון נתוני השירות
        updated_models = self.test_models + [new_model]
        self.mock_llm_service.get_all_models.return_value = updated_models
        self.models_by_id["model-4"] = new_model
        
        # רענון הבוחר
        self.model_selector.refresh_models()
        
        # בדיקת שהמודל החדש נוסף
        self.assertIn("model-4", self.model_selector.model_items)
        
        # בחירת המודל החדש
        self.model_selector.on_model_item_selected("model-4")
        
        # בדיקת שהפרטים מציגים את המודל החדש
        self.assertEqual(self.model_details.current_model.id, "model-4")
        self.assertEqual(self.model_details.name_value.text(), "Model 4")


if __name__ == '__main__':
    unittest.main()