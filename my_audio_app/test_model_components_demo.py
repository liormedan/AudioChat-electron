"""
הדגמה של רכיבי ModelSelector ו-ModelDetails
"""

import sys
import os

# הוספת נתיב לקבצי המקור
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QSplitter
from PyQt6.QtCore import Qt

from ui.components.llm.model_selector import ModelSelector
from ui.components.llm.model_details import ModelDetailsWidget
from models.llm_models import LLMModel, LLMProvider, ModelCapability
from services.llm_service import LLMService


class ModelComponentsDemo(QMainWindow):
    """חלון הדגמה לרכיבי מודל"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Model Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # יצירת שירות LLM עם נתונים דמה
        self.llm_service = self.create_demo_service()
        
        self.setup_ui()
        self.connect_signals()
    
    def create_demo_service(self):
        """יצירת שירות LLM עם נתוני הדגמה"""
        # יצירת שירות אמיתי עם מסד נתונים זמני
        service = LLMService(":memory:")
        
        # הוספת מודלים נוספים להדגמה
        demo_models = [
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
                is_available=True
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
        
        # שמירת המודלים
        for model in demo_models:
            service.save_model(model)
        
        # הגדרת מודל פעיל
        service.set_active_model("demo-gpt-4")
        
        return service
    
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
        
        # עדכון תצוגת הבוחר
        self.model_selector.on_model_activated(model_id)


def main():
    """פונקציה ראשית"""
    app = QApplication(sys.argv)
    
    # יצירת חלון הדגמה
    demo = ModelComponentsDemo()
    demo.show()
    
    # הרצת האפליקציה
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
