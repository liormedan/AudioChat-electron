"""
בדיקות יחידה לרכיב ModelDetails
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

from ui.components.llm.model_details import ModelDetailsWidget, ModelComparisonDialog, ModelPerformanceWidget
from models.llm_models import LLMModel, LLMProvider, ModelCapability
from services.llm_service import LLMService


class TestModelPerformanceWidget(unittest.TestCase):
    """בדיקות לרכיב ביצועי מודל"""
    
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
        
        self.performance_widget = ModelPerformanceWidget(self.test_model)
    
    def test_performance_widget_creation(self):
        """בדיקת יצירת רכיב ביצועים"""
        self.assertIsNotNone(self.performance_widget)
        self.assertEqual(self.performance_widget.model, self.test_model)
    
    def test_performance_metrics_display(self):
        """בדיקת תצוגת מטריקות ביצועים"""
        # בדיקת שהתוויות קיימות
        self.assertIsNotNone(self.performance_widget.response_time_value)
        self.assertIsNotNone(self.performance_widget.success_rate_value)
        self.assertIsNotNone(self.performance_widget.monthly_usage_value)
        self.assertIsNotNone(self.performance_widget.monthly_cost_value)
        
        # בדיקת ערכי ברירת מחדל
        self.assertEqual(self.performance_widget.response_time_value.text(), "טוען...")
        self.assertEqual(self.performance_widget.success_rate_value.text(), "טוען...")
    
    def test_performance_data_update(self):
        """בדיקת עדכון נתוני ביצועים"""
        # הדמיית עדכון נתונים
        self.performance_widget.update_performance_data()
        
        # בדיקת שהנתונים עודכנו
        self.assertNotEqual(self.performance_widget.response_time_value.text(), "טוען...")
        self.assertNotEqual(self.performance_widget.success_rate_value.text(), "טוען...")


class TestModelComparisonDialog(unittest.TestCase):
    """בדיקות לדיאלוג השוואת מודלים"""
    
    @classmethod
    def setUpClass(cls):
        """הגדרה לכל הבדיקות"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לכל בדיקה"""
        self.test_models = [
            LLMModel(
                id="model-1",
                name="Model 1",
                provider="TestProvider",
                description="First test model",
                max_tokens=2048,
                cost_per_token=0.00002,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
                is_active=True,
                is_available=True,
                version="1.0"
            ),
            LLMModel(
                id="model-2",
                name="Model 2",
                provider="TestProvider",
                description="Second test model",
                max_tokens=4096,
                cost_per_token=0.00003,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                is_active=False,
                is_available=True,
                version="2.0"
            )
        ]
        
        self.comparison_dialog = ModelComparisonDialog(self.test_models)
    
    def test_comparison_dialog_creation(self):
        """בדיקת יצירת דיאלוג השוואה"""
        self.assertIsNotNone(self.comparison_dialog)
        self.assertEqual(self.comparison_dialog.models, self.test_models)
    
    def test_comparison_table_setup(self):
        """בדיקת הגדרת טבלת השוואה"""
        table = self.comparison_dialog.comparison_table
        
        # בדיקת מספר עמודות
        self.assertEqual(table.columnCount(), len(self.test_models))
        
        # בדיקת כותרות עמודות
        for i, model in enumerate(self.test_models):
            header_text = table.horizontalHeaderItem(i).text()
            self.assertEqual(header_text, model.name)
        
        # בדיקת שיש שורות
        self.assertGreater(table.rowCount(), 0)
    
    def test_comparison_data_display(self):
        """בדיקת תצוגת נתוני השוואה"""
        table = self.comparison_dialog.comparison_table
        
        # בדיקת שהנתונים מוצגים בטבלה
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                self.assertIsNotNone(item)
                self.assertNotEqual(item.text(), "")
    
    def test_empty_models_list(self):
        """בדיקת רשימת מודלים ריקה"""
        empty_dialog = ModelComparisonDialog([])
        table = empty_dialog.comparison_table
        
        # בדיקת שהטבלה ריקה
        self.assertEqual(table.columnCount(), 0)


class TestModelDetailsWidget(unittest.TestCase):
    """בדיקות לרכיב פרטי מודל"""
    
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
        self.test_model = LLMModel(
            id="test-model-1",
            name="Test Model",
            provider="TestProvider",
            description="A comprehensive test model for unit testing with various capabilities",
            max_tokens=2048,
            cost_per_token=0.00002,
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT, ModelCapability.CODE_GENERATION],
            is_active=False,
            is_available=True,
            context_window=4096,
            version="1.0",
            training_data_cutoff="2023-04-01",
            metadata={"test_key": "test_value", "another_key": "another_value"}
        )
        
        self.provider_models = [
            self.test_model,
            LLMModel(
                id="test-model-2",
                name="Test Model 2",
                provider="TestProvider",
                description="Second test model",
                max_tokens=4096,
                cost_per_token=0.00003,
                capabilities=[ModelCapability.TEXT_GENERATION],
                is_active=False,
                is_available=True
            )
        ]
        
        # הגדרת התנהגות השירות המדומה
        self.mock_llm_service.get_model.return_value = self.test_model
        self.mock_llm_service.get_models_by_provider.return_value = self.provider_models
        self.mock_llm_service.set_active_model.return_value = True
        
        # יצירת רכיב
        self.model_details = ModelDetailsWidget(self.mock_llm_service)
    
    def test_model_details_creation(self):
        """בדיקת יצירת רכיב פרטי מודל"""
        self.assertIsNotNone(self.model_details)
        self.assertEqual(self.model_details.llm_service, self.mock_llm_service)
        self.assertIsNone(self.model_details.current_model)
    
    def test_empty_state_display(self):
        """בדיקת תצוגת מצב ריק"""
        self.model_details.show_empty_state()
        
        # בדיקת שהכותרת מציגה הודעת ברירת מחדל
        self.assertEqual(self.model_details.title_label.text(), "בחר מודל לצפייה בפרטים")
        
        # בדיקת שהכפתורים מושבתים
        self.assertFalse(self.model_details.activate_button.isEnabled())
        self.assertFalse(self.model_details.compare_button.isEnabled())
        
        # בדיקת שהשדות מאופסים
        self.assertEqual(self.model_details.name_value.text(), "-")
        self.assertEqual(self.model_details.provider_value.text(), "-")
    
    def test_show_model_details(self):
        """בדיקת הצגת פרטי מודל"""
        # הצגת פרטי מודל
        self.model_details.show_model_details("test-model-1")
        
        # בדיקת שהשירות נקרא
        self.mock_llm_service.get_model.assert_called_once_with("test-model-1")
        
        # בדיקת שהמודל הנוכחי עודכן
        self.assertEqual(self.model_details.current_model, self.test_model)
        
        # בדיקת עדכון כותרת
        self.assertEqual(self.model_details.title_label.text(), f"פרטי מודל: {self.test_model.name}")
        
        # בדיקת עדכון מידע בסיסי
        self.assertEqual(self.model_details.name_value.text(), self.test_model.name)
        self.assertEqual(self.model_details.provider_value.text(), self.test_model.provider)
        self.assertEqual(self.model_details.version_value.text(), self.test_model.version)
        
        # בדיקת עדכון תיאור
        self.assertEqual(self.model_details.description_text.toPlainText(), self.test_model.description)
        
        # בדיקת עדכון מפרטים טכניים
        self.assertEqual(self.model_details.max_tokens_value.text(), f"{self.test_model.max_tokens:,}")
        self.assertEqual(self.model_details.context_window_value.text(), f"{self.test_model.context_window:,}")
        
        # בדיקת עדכון יכולות
        self.assertEqual(self.model_details.capabilities_text.toPlainText(), self.test_model.capabilities_display)
        
        # בדיקת עדכון הגדרות
        self.assertEqual(self.model_details.training_cutoff_value.text(), self.test_model.training_data_cutoff)
        
        # בדיקת כפתורים
        self.assertTrue(self.model_details.activate_button.isEnabled())  # מודל לא פעיל
        self.assertTrue(self.model_details.compare_button.isEnabled())
    
    def test_show_active_model_details(self):
        """בדיקת הצגת פרטי מודל פעיל"""
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
        
        self.mock_llm_service.get_model.return_value = active_model
        
        # הצגת פרטי מודל פעיל
        self.model_details.show_model_details("active-model")
        
        # בדיקת שכפתור ההפעלה מושבת
        self.assertFalse(self.model_details.activate_button.isEnabled())
        
        # בדיקת תצוגת סטטוס
        self.assertEqual(self.model_details.status_value.text(), "🟢 פעיל")
    
    def test_show_unavailable_model_details(self):
        """בדיקת הצגת פרטי מודל לא זמין"""
        # הגדרת מודל כלא זמין
        unavailable_model = LLMModel(
            id="unavailable-model",
            name="Unavailable Model",
            provider="TestProvider",
            description="Unavailable test model",
            max_tokens=2048,
            cost_per_token=0.00002,
            capabilities=[ModelCapability.TEXT_GENERATION],
            is_active=False,
            is_available=False
        )
        
        self.mock_llm_service.get_model.return_value = unavailable_model
        
        # הצגת פרטי מודל לא זמין
        self.model_details.show_model_details("unavailable-model")
        
        # בדיקת תצוגת סטטוס
        self.assertEqual(self.model_details.status_value.text(), "🔴 לא זמין")
    
    def test_activate_model(self):
        """בדיקת הפעלת מודל"""
        # הגדרת מודל נוכחי
        self.model_details.current_model = self.test_model
        
        # הפעלת מודל
        self.model_details.activate_model()
        
        # בדיקת שהשירות נקרא
        self.mock_llm_service.set_active_model.assert_called_once_with(self.test_model.id)
    
    def test_activate_model_without_current_model(self):
        """בדיקת הפעלת מודל ללא מודל נוכחי"""
        # איפוס מודל נוכחי
        self.model_details.current_model = None
        
        # הפעלת מודל
        self.model_details.activate_model()
        
        # בדיקת שהשירות לא נקרא
        self.mock_llm_service.set_active_model.assert_not_called()
    
    def test_show_comparison(self):
        """בדיקת הצגת השוואה"""
        # הגדרת מודל נוכחי
        self.model_details.current_model = self.test_model
        
        # הדמיית הצגת השוואה
        with patch('ui.components.llm.model_details.ModelComparisonDialog') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog.return_value = mock_dialog_instance
            
            self.model_details.show_comparison()
            
            # בדיקת שהדיאלוג נוצר
            mock_dialog.assert_called_once()
            mock_dialog_instance.exec.assert_called_once()
    
    def test_show_comparison_without_current_model(self):
        """בדיקת הצגת השוואה ללא מודל נוכחי"""
        # איפוס מודל נוכחי
        self.model_details.current_model = None
        
        # הדמיית הצגת השוואה
        with patch('ui.components.llm.model_details.ModelComparisonDialog') as mock_dialog:
            self.model_details.show_comparison()
            
            # בדיקת שהדיאלוג לא נוצר
            mock_dialog.assert_not_called()
    
    def test_show_comparison_no_other_models(self):
        """בדיקת השוואה ללא מודלים נוספים"""
        # הגדרת מודל נוכחי
        self.model_details.current_model = self.test_model
        
        # הגדרת רק מודל אחד
        self.mock_llm_service.get_models_by_provider.return_value = [self.test_model]
        
        # הדמיית הצגת השוואה
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msg:
            self.model_details.show_comparison()
            
            # בדיקת שהודעה הוצגה
            mock_msg.assert_called_once()
    
    def test_model_details_with_metadata(self):
        """בדיקת הצגת מטא-נתונים"""
        # הצגת פרטי מודל עם מטא-נתונים
        self.model_details.show_model_details("test-model-1")
        
        # בדיקת שהמטא-נתונים מוצגים
        metadata_text = self.model_details.metadata_text.toPlainText()
        self.assertIn("test_key: test_value", metadata_text)
        self.assertIn("another_key: another_value", metadata_text)
    
    def test_model_details_without_metadata(self):
        """בדיקת הצגת מודל ללא מטא-נתונים"""
        # יצירת מודל ללא מטא-נתונים
        model_without_metadata = LLMModel(
            id="no-metadata-model",
            name="No Metadata Model",
            provider="TestProvider",
            description="Model without metadata",
            max_tokens=2048,
            cost_per_token=0.00002,
            capabilities=[ModelCapability.TEXT_GENERATION],
            metadata={}
        )
        
        self.mock_llm_service.get_model.return_value = model_without_metadata
        
        # הצגת פרטי מודל
        self.model_details.show_model_details("no-metadata-model")
        
        # בדיקת הודעת ברירת מחדל
        self.assertEqual(self.model_details.metadata_text.toPlainText(), "אין מטא-נתונים זמינים")
    
    def test_add_to_comparison(self):
        """בדיקת הוספה להשוואה"""
        # הוספת מודלים להשוואה
        self.model_details.add_to_comparison("model-1")
        self.model_details.add_to_comparison("model-2")
        
        # בדיקת שהמודלים נוספו
        self.assertIn("model-1", self.model_details.comparison_models)
        self.assertIn("model-2", self.model_details.comparison_models)
    
    def test_add_to_comparison_limit(self):
        """בדיקת הגבלת מספר מודלים להשוואה"""
        # הוספת יותר מ-3 מודלים
        for i in range(5):
            self.model_details.add_to_comparison(f"model-{i}")
        
        # בדיקת שרק 3 מודלים אחרונים נשמרו
        self.assertEqual(len(self.model_details.comparison_models), 3)
        self.assertIn("model-2", self.model_details.comparison_models)
        self.assertIn("model-3", self.model_details.comparison_models)
        self.assertIn("model-4", self.model_details.comparison_models)
    
    def test_clear_comparison(self):
        """בדיקת ניקוי השוואה"""
        # הוספת מודלים להשוואה
        self.model_details.add_to_comparison("model-1")
        self.model_details.add_to_comparison("model-2")
        
        # ניקוי השוואה
        self.model_details.clear_comparison()
        
        # בדיקת שהרשימה ריקה
        self.assertEqual(len(self.model_details.comparison_models), 0)
    
    def test_model_activation_signal(self):
        """בדיקת אות הפעלת מודל"""
        signal_received = False
        received_model_id = None
        
        def on_model_activated(model_id):
            nonlocal signal_received, received_model_id
            signal_received = True
            received_model_id = model_id
        
        self.model_details.model_activated.connect(on_model_activated)
        
        # הגדרת מודל נוכחי והפעלה
        self.model_details.current_model = self.test_model
        self.model_details.activate_model()
        
        # בדיקת שהאות נשלח
        self.assertTrue(signal_received)
        self.assertEqual(received_model_id, self.test_model.id)


if __name__ == '__main__':
    unittest.main()
