"""
דוגמה לשימוש בשירות LLM עם ניהול מפתחות מאובטח
מדגים את השילוב המלא בין השירותים
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QTextEdit, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

# הוספת נתיב למודלים
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import LLMService
from ui.components.llm.api_key_dialog import APIKeyDialog


class LLMSecureDemo(QMainWindow):
    """דמו לשירות LLM עם ניהול מפתחות מאובטח"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Service with Secure API Key Management")
        self.setGeometry(100, 100, 800, 600)
        
        # יצירת שירות LLM (כולל מנהל מפתחות מאובטח)
        self.llm_service = LLMService()
        
        self.setup_ui()
        self.setup_connections()
        self.update_status()
        
        # עדכון סטטוס כל 30 שניות
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(30000)  # 30 שניות
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # כותרת
        title = QLabel("LLM Service with Secure API Key Management")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # קבוצת ניהול ספקים
        providers_group = QGroupBox("Provider Management")
        providers_layout = QVBoxLayout(providers_group)
        
        # בחירת ספק
        provider_selection_layout = QHBoxLayout()
        
        provider_selection_layout.addWidget(QLabel("Select Provider:"))
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Google", "Cohere"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_selection_layout.addWidget(self.provider_combo)
        
        # כפתורי ניהול ספק
        self.manage_key_button = QPushButton("🔑 Manage API Key")
        self.manage_key_button.clicked.connect(self.manage_current_provider_key)
        provider_selection_layout.addWidget(self.manage_key_button)
        
        self.test_connection_button = QPushButton("🧪 Test Connection")
        self.test_connection_button.clicked.connect(self.test_current_provider)
        provider_selection_layout.addWidget(self.test_connection_button)
        
        providers_layout.addLayout(provider_selection_layout)
        
        # סטטוס ספק נוכחי
        self.provider_status_label = QLabel()
        self.provider_status_label.setStyleSheet("font-size: 12px; margin: 10px;")
        providers_layout.addWidget(self.provider_status_label)
        
        layout.addWidget(providers_group)
        
        # קבוצת מודלים
        models_group = QGroupBox("Model Selection")
        models_layout = QVBoxLayout(models_group)
        
        model_selection_layout = QHBoxLayout()
        
        model_selection_layout.addWidget(QLabel("Available Models:"))
        
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_selection_layout.addWidget(self.model_combo)
        
        self.set_active_button = QPushButton("✅ Set Active")
        self.set_active_button.clicked.connect(self.set_active_model)
        model_selection_layout.addWidget(self.set_active_button)
        
        models_layout.addLayout(model_selection_layout)
        
        # מודל פעיל נוכחי
        self.active_model_label = QLabel()
        self.active_model_label.setStyleSheet("font-size: 12px; margin: 10px;")
        models_layout.addWidget(self.active_model_label)
        
        layout.addWidget(models_group)
        
        # קבוצת סטטוס אבטחה
        security_group = QGroupBox("Security Status")
        security_layout = QVBoxLayout(security_group)
        
        self.security_status_text = QTextEdit()
        self.security_status_text.setMaximumHeight(150)
        self.security_status_text.setReadOnly(True)
        security_layout.addWidget(self.security_status_text)
        
        security_buttons_layout = QHBoxLayout()
        
        refresh_security_button = QPushButton("🔄 Refresh Security Status")
        refresh_security_button.clicked.connect(self.update_security_status)
        security_buttons_layout.addWidget(refresh_security_button)
        
        cleanup_button = QPushButton("🧹 Cleanup Old Data")
        cleanup_button.clicked.connect(self.cleanup_old_data)
        security_buttons_layout.addWidget(cleanup_button)
        
        security_layout.addLayout(security_buttons_layout)
        
        layout.addWidget(security_group)
        
        # לוג פעילות
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setReadOnly(True)
        log_layout.addWidget(self.activity_log)
        
        clear_log_button = QPushButton("🗑️ Clear Log")
        clear_log_button.clicked.connect(self.activity_log.clear)
        log_layout.addWidget(clear_log_button)
        
        layout.addWidget(log_group)
        
        # עיצוב כללי
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                color: #ffffff;
            }
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #555;
                color: #ffffff;
                padding: 4px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def setup_connections(self):
        """הגדרת חיבורים לאותות"""
        # אותות שירות LLM
        self.llm_service.provider_connected.connect(self.on_provider_connected)
        self.llm_service.provider_disconnected.connect(self.on_provider_disconnected)
        self.llm_service.model_activated.connect(self.on_model_activated)
        
        # אותות מנהל מפתחות API
        self.llm_service.api_key_manager.key_added.connect(self.on_api_key_added)
        self.llm_service.api_key_manager.key_updated.connect(self.on_api_key_updated)
        self.llm_service.api_key_manager.key_deleted.connect(self.on_api_key_deleted)
        self.llm_service.api_key_manager.key_tested.connect(self.on_api_key_tested)
    
    def log_activity(self, message: str):
        """הוספת הודעה ללוג פעילות"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.append(f"[{timestamp}] {message}")
    
    def update_status(self):
        """עדכון סטטוס כללי"""
        self.update_provider_status()
        self.update_models_list()
        self.update_active_model()
        self.update_security_status()
    
    def update_provider_status(self):
        """עדכון סטטוס ספק נוכחי"""
        current_provider = self.provider_combo.currentText()
        provider = self.llm_service.get_provider(current_provider)
        
        if provider:
            status_text = f"Status: {provider.status_display}\n"
            
            # בדיקה אם יש מפתח API שמור
            has_key = self.llm_service.get_provider_api_key(current_provider) is not None
            status_text += f"API Key: {'✅ Stored' if has_key else '❌ Not configured'}\n"
            
            if provider.last_test_date:
                status_text += f"Last Test: {provider.last_test_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if provider.error_message:
                status_text += f"Error: {provider.error_message}"
            
            self.provider_status_label.setText(status_text)
            
            # עדכון מצב כפתורים
            self.test_connection_button.setEnabled(has_key)
        else:
            self.provider_status_label.setText("Provider not found")
            self.test_connection_button.setEnabled(False)
    
    def update_models_list(self):
        """עדכון רשימת מודלים"""
        current_provider = self.provider_combo.currentText()
        models = self.llm_service.get_models_by_provider(current_provider)
        
        self.model_combo.clear()
        for model in models:
            self.model_combo.addItem(f"{model.name} ({model.id})", model.id)
        
        self.set_active_button.setEnabled(len(models) > 0)
    
    def update_active_model(self):
        """עדכון מודל פעיל"""
        active_model = self.llm_service.get_active_model()
        
        if active_model:
            self.active_model_label.setText(
                f"Active Model: {active_model.display_name}\n"
                f"Max Tokens: {active_model.max_tokens:,}\n"
                f"Cost per 1K tokens: ${active_model.cost_per_1k_tokens:.4f}"
            )
        else:
            self.active_model_label.setText("No active model selected")
    
    def update_security_status(self):
        """עדכון סטטוס אבטחה"""
        status = self.llm_service.get_api_key_security_status()
        stored_providers = self.llm_service.get_stored_api_key_providers()
        
        status_text = f"🔒 Security Status:\n"
        status_text += f"• Active API Keys: {status['active_keys_count']}\n"
        status_text += f"• Encryption: {'✅ Enabled' if status['encryption_enabled'] else '❌ Disabled'}\n\n"
        
        if stored_providers:
            status_text += "📋 Stored Providers:\n"
            for provider in stored_providers:
                last_used = provider.get('last_used', 'Never')
                if last_used and last_used != 'Never':
                    last_used = last_used[:19].replace('T', ' ')
                
                status_text += f"• {provider['provider_name']}: {last_used}\n"
        else:
            status_text += "No API keys stored"
        
        self.security_status_text.setPlainText(status_text)
    
    def on_provider_changed(self):
        """טיפול בשינוי ספק"""
        self.update_provider_status()
        self.update_models_list()
        self.log_activity(f"Selected provider: {self.provider_combo.currentText()}")
    
    def on_model_changed(self):
        """טיפול בשינוי מודל"""
        model_id = self.model_combo.currentData()
        if model_id:
            self.log_activity(f"Selected model: {model_id}")
    
    def manage_current_provider_key(self):
        """ניהול מפתח API לספק נוכחי"""
        current_provider = self.provider_combo.currentText()
        dialog = APIKeyDialog(current_provider, self.llm_service.api_key_manager, self)
        dialog.exec()
        
        # עדכון סטטוס אחרי סגירת הדיאלוג
        self.update_status()
    
    def test_current_provider(self):
        """בדיקת חיבור לספק נוכחי"""
        current_provider = self.provider_combo.currentText()
        
        self.test_connection_button.setEnabled(False)
        self.test_connection_button.setText("🔄 Testing...")
        
        # בדיקת חיבור
        success = self.llm_service.test_provider_connection(current_provider)
        
        # החזרת מצב כפתור
        self.test_connection_button.setEnabled(True)
        self.test_connection_button.setText("🧪 Test Connection")
        
        # הודעה למשתמש
        if success:
            QMessageBox.information(self, "Success", f"Connection to {current_provider} successful!")
        else:
            provider = self.llm_service.get_provider(current_provider)
            error_msg = provider.error_message if provider else "Unknown error"
            QMessageBox.warning(self, "Connection Failed", f"Failed to connect to {current_provider}:\n{error_msg}")
    
    def set_active_model(self):
        """הגדרת מודל פעיל"""
        model_id = self.model_combo.currentData()
        if model_id:
            success = self.llm_service.set_active_model(model_id)
            if success:
                self.update_active_model()
                self.log_activity(f"Set active model: {model_id}")
                QMessageBox.information(self, "Success", f"Model {model_id} set as active!")
            else:
                QMessageBox.warning(self, "Error", "Failed to set active model")
    
    def cleanup_old_data(self):
        """ניקוי נתונים ישנים"""
        reply = QMessageBox.question(
            self, "Confirm Cleanup",
            "This will remove old API key test data and history.\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.llm_service.cleanup_old_api_key_data(30)  # שמירת 30 ימים אחרונים
            self.log_activity("Cleaned up old API key data")
            self.update_security_status()
            QMessageBox.information(self, "Success", "Old data cleaned up successfully!")
    
    # Event handlers for signals
    def on_provider_connected(self, provider_name: str):
        """טיפול בחיבור ספק"""
        self.log_activity(f"✅ Provider connected: {provider_name}")
        self.update_provider_status()
    
    def on_provider_disconnected(self, provider_name: str):
        """טיפול בניתוק ספק"""
        self.log_activity(f"❌ Provider disconnected: {provider_name}")
        self.update_provider_status()
    
    def on_model_activated(self, model_id: str):
        """טיפול בהפעלת מודל"""
        self.log_activity(f"🤖 Model activated: {model_id}")
        self.update_active_model()
    
    def on_api_key_added(self, provider_name: str):
        """טיפול בהוספת מפתח API"""
        self.log_activity(f"🔑 API key added for: {provider_name}")
        self.update_status()
    
    def on_api_key_updated(self, provider_name: str):
        """טיפול בעדכון מפתח API"""
        self.log_activity(f"🔄 API key updated for: {provider_name}")
        self.update_status()
    
    def on_api_key_deleted(self, provider_name: str):
        """טיפול במחיקת מפתח API"""
        self.log_activity(f"🗑️ API key deleted for: {provider_name}")
        self.update_status()
    
    def on_api_key_tested(self, provider_name: str, success: bool):
        """טיפול בבדיקת מפתח API"""
        status = "✅ Success" if success else "❌ Failed"
        self.log_activity(f"🧪 API key test for {provider_name}: {status}")


def main():
    """הרצת הדמו"""
    app = QApplication(sys.argv)
    
    window = LLMSecureDemo()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
