"""
בדיקה פשוטה לרכיב ProviderCard
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

# הוספת נתיב
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.llm_models import LLMProvider, ProviderStatus
from services.llm_service import LLMService
from ui.components.llm.provider_card import ProviderCard
from datetime import datetime


class SimpleTestWindow(QMainWindow):
    """חלון בדיקה פשוט"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Provider Card Simple Test")
        self.setGeometry(100, 100, 800, 400)
        
        # יצירת שירות LLM
        self.llm_service = LLMService()
        
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
        title = QLabel("Provider Cards Test - Different States")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # יצירת כרטיסים עם סטטוסים שונים
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # כרטיס מחובר
        connected_provider = LLMProvider(
            name="OpenAI",
            api_base_url="https://api.openai.com/v1",
            supported_models=["GPT-4", "GPT-3.5-turbo"],
            connection_status=ProviderStatus.CONNECTED,
            is_connected=True,
            last_test_date=datetime.now(),
            rate_limit=3500,
            cost_per_1k_tokens=0.03
        )
        
        connected_card = ProviderCard(connected_provider, self.llm_service)
        connected_card.connection_changed.connect(self.on_connection_changed)
        cards_layout.addWidget(connected_card)
        
        # כרטיס מנותק
        disconnected_provider = LLMProvider(
            name="Anthropic",
            api_base_url="https://api.anthropic.com/v1",
            supported_models=["Claude-3-Opus", "Claude-3-Sonnet"],
            connection_status=ProviderStatus.DISCONNECTED,
            is_connected=False,
            rate_limit=1000,
            cost_per_1k_tokens=0.015
        )
        
        disconnected_card = ProviderCard(disconnected_provider, self.llm_service)
        disconnected_card.connection_changed.connect(self.on_connection_changed)
        cards_layout.addWidget(disconnected_card)
        
        # כרטיס עם שגיאה
        error_provider = LLMProvider(
            name="Google",
            api_base_url="https://generativelanguage.googleapis.com/v1",
            supported_models=["Gemini-Pro"],
            connection_status=ProviderStatus.ERROR,
            is_connected=False,
            error_message="Invalid API key format",
            rate_limit=60,
            cost_per_1k_tokens=0.001
        )
        
        error_card = ProviderCard(error_provider, self.llm_service)
        error_card.connection_changed.connect(self.on_connection_changed)
        cards_layout.addWidget(error_card)
        
        cards_layout.addStretch()
        layout.addLayout(cards_layout)
        
        # הודעות סטטוס
        self.status_label = QLabel("Status messages will appear here...")
        self.status_label.setStyleSheet("color: #888; font-size: 12px; margin-top: 20px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def on_connection_changed(self, provider_name: str, is_connected: bool):
        """טיפול בשינוי חיבור"""
        status = "Connected" if is_connected else "Disconnected"
        message = f"Provider {provider_name} is now {status}"
        self.status_label.setText(message)
        print(message)


def main():
    """פונקציה ראשית"""
    app = QApplication(sys.argv)
    
    # הגדרת עיצוב כללי
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }
    """)
    
    window = SimpleTestWindow()
    window.show()
    
    print("Provider Card test window opened. You can:")
    print("- Click on cards to connect/configure")
    print("- Right-click for context menu")
    print("- Test connection functionality")
    print("- Close window to exit")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()