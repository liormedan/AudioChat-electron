"""
בדיקות לרכיב ProviderCard
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt

# הוספת נתיב למודלים
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
app_dir = os.path.dirname(src_dir)
sys.path.append(app_dir)

from src.models.llm_models import LLMProvider, ProviderStatus
from src.services.llm_service import LLMService
from src.ui.components.llm.provider_card import ProviderCard


class TestProviderCardWindow(QMainWindow):
    """חלון בדיקה לרכיב ProviderCard"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Provider Card Test")
        self.setGeometry(100, 100, 1000, 600)
        
        # יצירת שירות LLM
        self.llm_service = LLMService()
        
        # הגדרת ממשק המשתמש
        self.setup_ui()
        
        # עיצוב כללי
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # כותרת
        from PyQt6.QtWidgets import QLabel
        title = QLabel("Provider Cards Test")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # יצירת כרטיסי ספקים לדוגמה
        providers_layout = QHBoxLayout()
        providers_layout.setSpacing(20)
        
        # קבלת ספקים מהשירות
        providers = self.llm_service.get_all_providers()
        
        # אם אין ספקים, יצירת דוגמאות
        if not providers:
            providers = self.create_sample_providers()
        
        # יצירת כרטיסים
        for provider in providers[:4]:  # הצגת 4 ראשונים
            card = ProviderCard(provider, self.llm_service)
            
            # חיבור לאותות
            card.connection_changed.connect(self.on_connection_changed)
            card.configuration_requested.connect(self.on_configuration_requested)
            card.test_requested.connect(self.on_test_requested)
            
            providers_layout.addWidget(card)
        
        providers_layout.addStretch()
        layout.addLayout(providers_layout)
        
        # שורה שנייה של כרטיסים (אם יש יותר ספקים)
        if len(providers) > 4:
            providers_layout2 = QHBoxLayout()
            providers_layout2.setSpacing(20)
            
            for provider in providers[4:8]:
                card = ProviderCard(provider, self.llm_service)
                
                # חיבור לאותות
                card.connection_changed.connect(self.on_connection_changed)
                card.configuration_requested.connect(self.on_configuration_requested)
                card.test_requested.connect(self.on_test_requested)
                
                providers_layout2.addWidget(card)
            
            providers_layout2.addStretch()
            layout.addLayout(providers_layout2)
        
        layout.addStretch()
    
    def create_sample_providers(self):
        """יצירת ספקים לדוגמה"""
        from datetime import datetime
        
        providers = [
            LLMProvider(
                name="OpenAI",
                api_base_url="https://api.openai.com/v1",
                supported_models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                connection_status=ProviderStatus.CONNECTED,
                is_connected=True,
                last_test_date=datetime.now(),
                rate_limit=3500,
                cost_per_1k_tokens=0.03
            ),
            LLMProvider(
                name="Anthropic",
                api_base_url="https://api.anthropic.com/v1",
                supported_models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                connection_status=ProviderStatus.DISCONNECTED,
                is_connected=False,
                rate_limit=1000,
                cost_per_1k_tokens=0.015
            ),
            LLMProvider(
                name="Google",
                api_base_url="https://generativelanguage.googleapis.com/v1",
                supported_models=["gemini-pro", "gemini-pro-vision"],
                connection_status=ProviderStatus.ERROR,
                is_connected=False,
                error_message="Invalid API key",
                rate_limit=60,
                cost_per_1k_tokens=0.001
            ),
            LLMProvider(
                name="Cohere",
                api_base_url="https://api.cohere.ai/v1",
                supported_models=["command", "command-light", "command-nightly"],
                connection_status=ProviderStatus.TESTING,
                is_connected=False,
                rate_limit=1000,
                cost_per_1k_tokens=0.002
            ),
            LLMProvider(
                name="Hugging Face",
                api_base_url="https://api-inference.huggingface.co",
                supported_models=["Various Open Source Models"],
                connection_status=ProviderStatus.DISCONNECTED,
                is_connected=False,
                rate_limit=100,
                cost_per_1k_tokens=0.0001
            )
        ]
        
        return providers
    
    def on_connection_changed(self, provider_name: str, is_connected: bool):
        """טיפול בשינוי חיבור"""
        status = "מחובר" if is_connected else "מנותק"
        print(f"Provider {provider_name} is now {status}")
    
    def on_configuration_requested(self, provider_name: str):
        """טיפול בבקשת הגדרה"""
        print(f"Configuration requested for {provider_name}")
    
    def on_test_requested(self, provider_name: str):
        """טיפול בבקשת בדיקה"""
        print(f"Test requested for {provider_name}")


def main():
    """פונקציה ראשית לבדיקה"""
    app = QApplication(sys.argv)
    
    # הגדרת עיצוב כללי
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }
    """)
    
    window = TestProviderCardWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
