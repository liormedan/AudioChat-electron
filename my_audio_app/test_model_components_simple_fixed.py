"""
הדגמה פשוטה של רכיבי ModelSelector ו-ModelDetails
"""

import sys
import os

# הוספת נתיב לקבצי המקור
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from ui.components.llm.model_selector import ModelSelector
from ui.components.llm.model_details import ModelDetailsWidget
from models.llm_models import LLMModel, LLMProvider, ModelCapability


class MockLLMService(QObject):
    """שירות LLM מדומה לבדיקות"""
    
    model_activated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.models = self._create_demo_models()
        self.providers = self._create_demo_providers()
        self.active_model_id = "demo-gpt-4"
    
    def _create_demo_models(self):
        """יצירת מודלים להדגמה"""
        return [
            LLMModel(
                id="demo-gpt-4",
                name="GPT-4 Demo",
                provider="OpenAI",
                description="מודל הדגמה מתקדם עם יכולות חזקות בהבנה ויצירה",
                max_tokens=8192,
                cost_per_token=0.00003,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT, ModelCapability.CODE_GENERATION],
                context_window=8192,
                version="4.0",
                is_available=True,
                is_active=True
            ),
            LLMModel(
                id="demo-claude-3",
                name="Claude 3 Demo",
                provider="Anthropic",
                description="מודל הדגמה עם יכולות חזקות בניתוח ויצירה",
                max_tokens=4096,
                cost_per_token=0.000015,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT, ModelCapability.SUMMARIZATION],
                context_window=200000,
                version="3.0",
                is_available=True
            ),
            LLMModel(
                id="demo-gemini-pro",
                name="Gemini Pro Demo",
                provider="Google",
                description="מודל הדגמה רב-תכליתי של Google",
                max_tokens=2048,
                cost_per_token=0.000001,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
                context_window=32768,
                version="1.0",
                is_available=True
            ),
            LLMModel(
                id="demo-unavailable",
                name="Unavailable Model",
                provider="TestProvider",
                description="מודל לא זמין להדגמה",
                max_tokens=1024,
                cost_per_token=0.00001,
                capabilities=[ModelCapability.TEXT_GENERATION],
                is_available=False
            )
        ]
    
    def _create_demo_providers(self):
        """יצירת ספקים להדגמה"""
        return [
            LLMProvider(
                name="OpenAI",
                api_base_url="https://api.openai.com/v1",
                supported_models=["demo-gpt-4"],
                is_connected=True
            ),
            LLMProvider(
                name="Anthropic",
                api_base_url="https://api.anthropic.com",
                supported_models=["demo-claude-3"],
                is_connected=True
            ),
            LLMProvider(
                name="Google",
                api_base_url="https://generativelanguage.googleapis.com",
                supported_models=["demo-gemini-pro"],
                is_connected=True
            )
        ]
    
    def get_all_models(self):
        """קבלת כל המודלים"""
        return self.models
    
    def get_all_providers(self):
        """קבלת כל הספקים"""
        return self.providers
    
    def get_model(self, model_id: str):
        """קבלת מודל לפי ID"""
        for model in self.models:
            if model.id == model_id:
                return model
        return None
    
    def get_active_model(self):
        """קבלת המודל הפעיל"""
        return self.get_model(self.active_model_id)
    
    def set_active_model(self, model_id: str):
        """הגדרת מודל פעיל"""
        # איפוס כל המודלים
        for model in self.models:
            model.is_active = False
        
        # הפעלת המודל הנבחר
        model = self.get_model(model_id)
        if model and model.is_available:
            model.is_active = True
            self.active_model_id = model_id
            return True
        return False
    
    def get_models_by_provider(self, provider_name: str):
        """קבלת מודלים לפי ספק"""
        return [model for model in self.models if model.provider == provider_name]


class ModelComponentsDemo(QMainWindow):
    """חלון הדגמה לרכיבי מודל"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Model Components Demo - LLM Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # יצירת שירות LLM מדומה
        self.llm_service = MockLLMService()
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # יצירת splitter לחלוקת המסך
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # יצירת רכיבים
        self.model_selector = ModelSelector(self.llm_service)
        self.model_details = ModelDetailsWidget(self.llm_service)
        
        # הוספת רכיבים ל-splitter
        splitter.addWidget(self.model_selector)
        splitter.addWidget(self.model_details)
        
        # הגדרת יחסי גודל
        splitter.setSizes([400, 800])
        
        # לייאאוט ראשי
        layout = QHBoxLayout(central_widget)
        layout.addWidget(splitter)
        
        # עיצוב כהה
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666;
            }
            QComboBox, QLineEdit {
                background-color: #404040;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 5px;
            }
            QTextEdit {
                background-color: #353535;
                border: 1px solid #666;
                border-radius: 4px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #404040;
                border: 1px solid #666;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
            }
            QScrollArea {
                border: none;
            }
            QFrame {
                border-radius: 6px;
            }
        """)
    
    def connect_signals(self):
        """חיבור אותות בין רכיבים"""
        # חיבור בחירת מודל לתצוגת פרטים
        self.model_selector.model_selected.connect(self.model_details.show_model_details)
        
        # חיבור הפעלת מודל
        self.model_selector.model_activated.connect(self.on_model_activated)
        self.model_details.model_activated.connect(self.on_model_activated)
    
    def on_model_activated(self, model_id: str):
        """טיפול בהפעלת מודל"""
        print(f"Model activated: {model_id}")
        
        # עדכון השירות
        success = self.llm_service.set_active_model(model_id)
        if success:
            # עדכון תצוגת הבוחר
            self.model_selector.on_model_activated(model_id)
            print(f"Successfully activated model: {model_id}")
        else:
            print(f"Failed to activate model: {model_id}")


def main():
    """פונקציה ראשית"""
    app = QApplication(sys.argv)
    
    try:
        # יצירת חלון הדגמה
        demo = ModelComponentsDemo()
        demo.show()
        
        print("Demo started successfully!")
        print("You can:")
        print("- Browse models in the left panel")
        print("- Filter by provider or capabilities")
        print("- Select a model to see details in the right panel")
        print("- Activate models using the buttons")
        
        # הרצת האפליקציה
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error starting demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
