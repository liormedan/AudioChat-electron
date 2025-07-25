"""
דוגמה לשימוש במנהל מפתחות API
מדגים את השילוב עם שירות LLM
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# הוספת נתיב למודלים
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.api_key_manager import APIKeyManager
from services.llm_service import LLMService
from ui.components.llm.api_key_dialog import APIKeyDialog


class APIKeyManagementDemo(QMainWindow):
    """דמו לניהול מפתחות API"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Key Management Demo")
        self.setGeometry(100, 100, 600, 400)
        
        # יצירת שירותים
        self.api_key_manager = APIKeyManager()
        self.llm_service = LLMService()
        
        self.setup_ui()
        self.setup_connections()
        self.update_status()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # כותרת
        title = QLabel("API Key Management Demo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # סטטוס
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # כפתורים לספקים
        providers = ["OpenAI", "Anthropic", "Google", "Cohere"]
        
        for provider in providers:
            button = QPushButton(f"Manage {provider} API Key")
            button.clicked.connect(lambda checked, p=provider: self.manage_provider_key(p))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 12px;
                    margin: 5px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            layout.addWidget(button)
        
        # כפתור סטטוס אבטחה
        security_button = QPushButton("🔒 Security Status")
        security_button.clicked.connect(self.show_security_status)
        security_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                margin: 5px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(security_button)
        
        # כפתור רענון
        refresh_button = QPushButton("🔄 Refresh Status")
        refresh_button.clicked.connect(self.update_status)
        layout.addWidget(refresh_button)
        
        # עיצוב כללי
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def setup_connections(self):
        """הגדרת חיבורים לאותות"""
        self.api_key_manager.key_added.connect(self.on_key_changed)
        self.api_key_manager.key_updated.connect(self.on_key_changed)
        self.api_key_manager.key_deleted.connect(self.on_key_changed)
        self.api_key_manager.key_tested.connect(self.on_key_tested)
    
    def manage_provider_key(self, provider_name: str):
        """פתיחת דיאלוג ניהול מפתח לספק"""
        dialog = APIKeyDialog(provider_name, self.api_key_manager, self)
        dialog.exec()
        
        # עדכון סטטוס אחרי סגירת הדיאלוג
        self.update_status()
    
    def update_status(self):
        """עדכון סטטוס מפתחות"""
        providers = self.api_key_manager.list_stored_providers()
        security_status = self.api_key_manager.get_security_status()
        
        status_text = f"Active API Keys: {security_status['active_keys_count']}\n"
        status_text += f"Encryption: {'✅ Enabled' if security_status['encryption_enabled'] else '❌ Disabled'}\n\n"
        
        if providers:
            status_text += "Stored Providers:\n"
            for provider in providers:
                last_used = provider.get('last_used', 'Never')
                if last_used and last_used != 'Never':
                    last_used = last_used[:19].replace('T', ' ')
                
                status_text += f"• {provider['provider_name']}: Last used {last_used}\n"
        else:
            status_text += "No API keys stored yet."
        
        self.status_label.setText(status_text)
    
    def on_key_changed(self, provider_name: str):
        """טיפול בשינוי מפתח"""
        print(f"API key changed for {provider_name}")
        self.update_status()
    
    def on_key_tested(self, provider_name: str, success: bool):
        """טיפול בבדיקת מפתח"""
        status = "✅ Success" if success else "❌ Failed"
        print(f"Connection test for {provider_name}: {status}")
    
    def show_security_status(self):
        """הצגת סטטוס אבטחה מפורט"""
        from PyQt6.QtWidgets import QMessageBox
        
        status = self.api_key_manager.get_security_status()
        
        message = f"""Security Status Report:
        
Active Keys: {status['active_keys_count']}
Encryption: {'Enabled' if status['encryption_enabled'] else 'Disabled'}
Database: {status['database_path']}

Last Connection Tests:"""
        
        for provider, test_info in status['last_connection_tests'].items():
            test_status = "✅ Success" if test_info['success'] else "❌ Failed"
            test_time = test_info['last_test'][:19].replace('T', ' ') if test_info['last_test'] else 'Never'
            message += f"\n• {provider}: {test_status} ({test_time})"
        
        QMessageBox.information(self, "Security Status", message)


def main():
    """הרצת הדמו"""
    app = QApplication(sys.argv)
    
    # הגדרת עיצוב כהה
    app.setStyleSheet("""
        QApplication {
            background-color: #1e1e1e;
            color: #ffffff;
        }
    """)
    
    window = APIKeyManagementDemo()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()