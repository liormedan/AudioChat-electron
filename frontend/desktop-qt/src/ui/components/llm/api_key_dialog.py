"""
דיאלוג לניהול מפתחות API
מספק ממשק משתמש ידידותי להזנת ועריכת מפתחות API
"""

import os
import sys
from typing import Optional, Dict, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QCheckBox, QProgressBar, QMessageBox, QTabWidget,
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

# הוספת נתיב למודלים
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from services.api_key_manager import APIKeyManager


class ConnectionTestWorker(QThread):
    """Worker thread לבדיקת חיבור"""
    
    test_completed = pyqtSignal(bool, str, float)  # success, message, response_time
    
    def __init__(self, api_key_manager: APIKeyManager, provider_name: str, api_key: str):
        super().__init__()
        self.api_key_manager = api_key_manager
        self.provider_name = provider_name
        self.api_key = api_key
    
    def run(self):
        """ביצוע בדיקת חיבור ברקע"""
        success, message, response_time = self.api_key_manager.test_api_key_connection(
            self.provider_name, self.api_key
        )
        self.test_completed.emit(success, message, response_time)


class APIKeyDialog(QDialog):
    """דיאלוג לניהול מפתח API"""
    
    def __init__(self, provider_name: str, api_key_manager: APIKeyManager, parent=None):
        super().__init__(parent)
        self.provider_name = provider_name
        self.api_key_manager = api_key_manager
        self.current_api_key = None
        self.test_worker = None
        
        self.setWindowTitle(f"API Key Management - {provider_name}")
        self.setModal(True)
        self.resize(500, 400)
        
        # טעינת מפתח קיים אם יש
        self.current_api_key = self.api_key_manager.retrieve_api_key(provider_name)
        
        self.setup_ui()
        self.setup_connections()
        self.load_existing_data()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # כותרת
        title_label = QLabel(f"API Key Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # מידע על הספק
        provider_label = QLabel(f"Provider: {self.provider_name}")
        provider_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(provider_label)
        
        # טאבים
        self.tab_widget = QTabWidget()
        
        # טאב הזנת מפתח
        self.key_input_tab = self.create_key_input_tab()
        self.tab_widget.addTab(self.key_input_tab, "🔑 API Key")
        
        # טאב בדיקת חיבור
        self.connection_test_tab = self.create_connection_test_tab()
        self.tab_widget.addTab(self.connection_test_tab, "🔍 Test Connection")
        
        # טאב היסטוריה
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📊 History")
        
        layout.addWidget(self.tab_widget)
        
        # כפתורי פעולה
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Save")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        self.test_button = QPushButton("🧪 Test")
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.delete_button = QPushButton("🗑️ Delete")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.test_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # עיצוב כללי
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom: 2px solid #4CAF50;
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
        """)
    
    def create_key_input_tab(self) -> QWidget:
        """יצירת טאב הזנת מפתח"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # קבוצת הזנת מפתח
        key_group = QGroupBox("API Key Input")
        key_layout = QFormLayout(key_group)
        
        # שדה הזנת מפתח
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText(f"Enter your {self.provider_name} API key...")
        self.api_key_input.textChanged.connect(self.on_api_key_changed)
        
        # כפתור הצגה/הסתרה
        self.show_hide_button = QPushButton("👁️ Show")
        self.show_hide_button.setFixedWidth(80)
        self.show_hide_button.clicked.connect(self.toggle_key_visibility)
        
        key_input_layout = QHBoxLayout()
        key_input_layout.addWidget(self.api_key_input)
        key_input_layout.addWidget(self.show_hide_button)
        
        key_layout.addRow("API Key:", key_input_layout)
        
        # סטטוס תקינות
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("font-size: 11px;")
        key_layout.addRow("Status:", self.validation_label)
        
        layout.addWidget(key_group)
        
        # קבוצת מידע על הספק
        info_group = QGroupBox("Provider Information")
        info_layout = QFormLayout(info_group)
        
        provider_info = self.get_provider_info()
        
        info_layout.addRow("API Documentation:", 
                          QLabel(f'<a href="{provider_info["docs_url"]}" style="color: #4CAF50;">{provider_info["docs_url"]}</a>'))
        info_layout.addRow("Key Format:", QLabel(provider_info["key_format"]))
        info_layout.addRow("Rate Limits:", QLabel(provider_info["rate_limits"]))
        
        layout.addWidget(info_group)
        
        # הוראות
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = QTextEdit()
        instructions_text.setMaximumHeight(100)
        instructions_text.setReadOnly(True)
        instructions_text.setPlainText(provider_info["instructions"])
        instructions_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                color: #cccccc;
                font-size: 11px;
            }
        """)
        
        instructions_layout.addWidget(instructions_text)
        layout.addWidget(instructions_group)
        
        layout.addStretch()
        return widget
    
    def create_connection_test_tab(self) -> QWidget:
        """יצירת טאב בדיקת חיבור"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # קבוצת בדיקת חיבור
        test_group = QGroupBox("Connection Test")
        test_layout = QVBoxLayout(test_group)
        
        # כפתור בדיקה
        self.run_test_button = QPushButton("🚀 Run Connection Test")
        self.run_test_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.run_test_button.clicked.connect(self.run_connection_test)
        
        test_layout.addWidget(self.run_test_button)
        
        # פס התקדמות
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        test_layout.addWidget(self.test_progress)
        
        # תוצאות בדיקה
        self.test_results = QTextEdit()
        self.test_results.setMaximumHeight(150)
        self.test_results.setReadOnly(True)
        self.test_results.setPlaceholderText("Test results will appear here...")
        test_layout.addWidget(self.test_results)
        
        layout.addWidget(test_group)
        
        # הגדרות בדיקה מתקדמות
        advanced_group = QGroupBox("Advanced Test Settings")
        advanced_layout = QFormLayout(advanced_group)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 60)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        advanced_layout.addRow("Timeout:", self.timeout_spin)
        
        self.auto_test_checkbox = QCheckBox("Auto-test on key change")
        self.auto_test_checkbox.setChecked(True)
        advanced_layout.addRow("", self.auto_test_checkbox)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        return widget
    
    def create_history_tab(self) -> QWidget:
        """יצירת טאב היסטוריה"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # טבלת היסטוריה
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Test Time", "Success", "Response Time", "Message"
        ])
        
        # הגדרת עמודות
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                alternate-background-color: #3d3d3d;
                selection-background-color: #4CAF50;
                gridline-color: #555;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.history_table)
        
        # כפתור רענון
        refresh_button = QPushButton("🔄 Refresh History")
        refresh_button.clicked.connect(self.load_history)
        layout.addWidget(refresh_button)
        
        return widget
    
    def setup_connections(self):
        """הגדרת חיבורים"""
        self.save_button.clicked.connect(self.save_api_key)
        self.test_button.clicked.connect(self.run_connection_test)
        self.delete_button.clicked.connect(self.delete_api_key)
        self.cancel_button.clicked.connect(self.reject)
        
        # חיבור לאותות של מנהל המפתחות
        self.api_key_manager.key_tested.connect(self.on_key_tested)
    
    def load_existing_data(self):
        """טעינת נתונים קיימים"""
        if self.current_api_key:
            # הצגת מפתח קיים (מוסתר)
            self.api_key_input.setText(self.current_api_key)
            self.validation_label.setText("✅ Valid key loaded")
            self.validation_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)
        
        # טעינת היסטוריה
        self.load_history()
    
    def get_provider_info(self) -> Dict[str, str]:
        """קבלת מידע על הספק"""
        provider_info = {
            "OpenAI": {
                "docs_url": "https://platform.openai.com/api-keys",
                "key_format": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "rate_limits": "3,500 RPM (varies by plan)",
                "instructions": "1. Go to OpenAI Platform\n2. Navigate to API Keys section\n3. Create new secret key\n4. Copy and paste here"
            },
            "Anthropic": {
                "docs_url": "https://console.anthropic.com/",
                "key_format": "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "rate_limits": "1,000 RPM (varies by plan)",
                "instructions": "1. Go to Anthropic Console\n2. Navigate to API Keys\n3. Generate new key\n4. Copy and paste here"
            },
            "Google": {
                "docs_url": "https://makersuite.google.com/app/apikey",
                "key_format": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "rate_limits": "60 RPM (free tier)",
                "instructions": "1. Go to Google AI Studio\n2. Get API key\n3. Copy and paste here"
            },
            "Cohere": {
                "docs_url": "https://dashboard.cohere.ai/api-keys",
                "key_format": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "rate_limits": "1,000 RPM (varies by plan)",
                "instructions": "1. Go to Cohere Dashboard\n2. Navigate to API Keys\n3. Create new key\n4. Copy and paste here"
            }
        }
        
        return provider_info.get(self.provider_name, {
            "docs_url": "https://example.com",
            "key_format": "Various formats",
            "rate_limits": "Varies by provider",
            "instructions": "Check provider documentation for API key generation instructions."
        })
    
    def on_api_key_changed(self):
        """טיפול בשינוי מפתח API"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            self.validation_label.setText("")
            self.save_button.setEnabled(False)
            self.test_button.setEnabled(False)
            return
        
        # בדיקת פורמט
        is_valid, message = self.api_key_manager.validate_api_key_format(self.provider_name, api_key)
        
        if is_valid:
            self.validation_label.setText("✅ Format valid")
            self.validation_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
            self.save_button.setEnabled(True)
            self.test_button.setEnabled(True)
            
            # בדיקה אוטומטית אם מופעלת
            if self.auto_test_checkbox.isChecked():
                QTimer.singleShot(1000, self.run_connection_test)  # דיליי של שנייה
        else:
            self.validation_label.setText(f"❌ {message}")
            self.validation_label.setStyleSheet("color: #f44336; font-size: 11px;")
            self.save_button.setEnabled(False)
            self.test_button.setEnabled(False)
    
    def toggle_key_visibility(self):
        """החלפת מצב הצגת מפתח"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_hide_button.setText("🙈 Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_hide_button.setText("👁️ Show")
    
    def run_connection_test(self):
        """הרצת בדיקת חיבור"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key first.")
            return
        
        # הצגת פס התקדמות
        self.test_progress.setVisible(True)
        self.test_progress.setRange(0, 0)  # אינסופי
        self.run_test_button.setEnabled(False)
        self.test_button.setEnabled(False)
        
        # הוספת הודעה לתוצאות
        self.test_results.append(f"🔄 Testing connection to {self.provider_name}...")
        
        # הרצת בדיקה ברקע
        self.test_worker = ConnectionTestWorker(self.api_key_manager, self.provider_name, api_key)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.start()
    
    def on_test_completed(self, success: bool, message: str, response_time: float):
        """טיפול בסיום בדיקת חיבור"""
        # הסתרת פס התקדמות
        self.test_progress.setVisible(False)
        self.run_test_button.setEnabled(True)
        self.test_button.setEnabled(True)
        
        # הצגת תוצאות
        status_icon = "✅" if success else "❌"
        time_str = f"{response_time:.2f}s"
        
        result_text = f"{status_icon} {message} (Response time: {time_str})"
        self.test_results.append(result_text)
        
        # עדכון היסטוריה
        self.load_history()
        
        # הודעה למשתמש
        if success:
            QMessageBox.information(self, "Success", f"Connection test successful!\nResponse time: {time_str}")
        else:
            QMessageBox.warning(self, "Test Failed", f"Connection test failed:\n{message}")
    
    def on_key_tested(self, provider_name: str, success: bool):
        """טיפול באות בדיקת מפתח"""
        if provider_name == self.provider_name:
            # עדכון היסטוריה
            self.load_history()
    
    def save_api_key(self):
        """שמירת מפתח API"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key.")
            return
        
        # בדיקת פורמט
        is_valid, message = self.api_key_manager.validate_api_key_format(self.provider_name, api_key)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Format", f"API key format is invalid:\n{message}")
            return
        
        # שמירה
        success = self.api_key_manager.store_api_key(self.provider_name, api_key)
        
        if success:
            QMessageBox.information(self, "Success", "API key saved successfully!")
            self.current_api_key = api_key
            self.delete_button.setEnabled(True)
            self.accept()  # סגירת הדיאלוג
        else:
            QMessageBox.critical(self, "Error", "Failed to save API key. Please try again.")
    
    def delete_api_key(self):
        """מחיקת מפתח API"""
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the API key for {self.provider_name}?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.api_key_manager.delete_api_key(self.provider_name)
            
            if success:
                QMessageBox.information(self, "Success", "API key deleted successfully!")
                self.current_api_key = None
                self.api_key_input.clear()
                self.delete_button.setEnabled(False)
                self.validation_label.setText("")
                self.load_history()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete API key. Please try again.")
    
    def load_history(self):
        """טעינת היסטוריית בדיקות"""
        history = self.api_key_manager.get_connection_test_history(self.provider_name, 20)
        
        self.history_table.setRowCount(len(history))
        
        for row, test in enumerate(history):
            # זמן בדיקה
            time_item = QTableWidgetItem(test["test_time"][:19].replace("T", " "))
            self.history_table.setItem(row, 0, time_item)
            
            # הצלחה
            success_text = "✅ Success" if test["success"] else "❌ Failed"
            success_item = QTableWidgetItem(success_text)
            if test["success"]:
                success_item.setForeground(Qt.GlobalColor.green)
            else:
                success_item.setForeground(Qt.GlobalColor.red)
            self.history_table.setItem(row, 1, success_item)
            
            # זמן תגובה
            response_time = f"{test['response_time']:.2f}s" if test["response_time"] else "N/A"
            time_item = QTableWidgetItem(response_time)
            self.history_table.setItem(row, 2, time_item)
            
            # הודעה
            message = test["error_message"] or "Connection successful"
            message_item = QTableWidgetItem(message)
            self.history_table.setItem(row, 3, message_item)
    
    def get_api_key(self) -> Optional[str]:
        """קבלת מפתח API שנשמר"""
        return self.current_api_key


class APIKeyRotationDialog(QDialog):
    """דיאלוג לרוטציה של מפתח API"""
    
    def __init__(self, provider_name: str, api_key_manager: APIKeyManager, parent=None):
        super().__init__(parent)
        self.provider_name = provider_name
        self.api_key_manager = api_key_manager
        
        self.setWindowTitle(f"API Key Rotation - {provider_name}")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # הסבר
        info_label = QLabel(
            "API Key rotation allows you to replace your current key with a new one.\n"
            "The old key will be deactivated and stored in history."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #cccccc; margin-bottom: 20px;")
        layout.addWidget(info_label)
        
        # מפתח חדש
        form_layout = QFormLayout()
        
        self.new_key_input = QLineEdit()
        self.new_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_key_input.setPlaceholderText("Enter new API key...")
        
        form_layout.addRow("New API Key:", self.new_key_input)
        
        # אישור מפתח
        self.confirm_key_input = QLineEdit()
        self.confirm_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_key_input.setPlaceholderText("Confirm new API key...")
        
        form_layout.addRow("Confirm Key:", self.confirm_key_input)
        
        layout.addLayout(form_layout)
        
        # סיבת רוטציה
        reason_group = QGroupBox("Rotation Reason")
        reason_layout = QVBoxLayout(reason_group)
        
        self.reason_combo = QComboBox()
        self.reason_combo.addItems([
            "Security rotation",
            "Key compromised",
            "Regular maintenance",
            "Other"
        ])
        
        reason_layout.addWidget(self.reason_combo)
        layout.addWidget(reason_group)
        
        # כפתורים
        buttons_layout = QHBoxLayout()
        
        self.rotate_button = QPushButton("🔄 Rotate Key")
        self.rotate_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        
        self.cancel_button = QPushButton("Cancel")
        
        buttons_layout.addWidget(self.rotate_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """הגדרת חיבורים"""
        self.rotate_button.clicked.connect(self.rotate_key)
        self.cancel_button.clicked.connect(self.reject)
        
        self.new_key_input.textChanged.connect(self.validate_inputs)
        self.confirm_key_input.textChanged.connect(self.validate_inputs)
    
    def validate_inputs(self):
        """בדיקת תקינות קלטים"""
        new_key = self.new_key_input.text().strip()
        confirm_key = self.confirm_key_input.text().strip()
        
        # בדיקה שהמפתחות זהים
        keys_match = new_key and new_key == confirm_key
        
        # בדיקת פורמט
        format_valid = False
        if new_key:
            format_valid, _ = self.api_key_manager.validate_api_key_format(self.provider_name, new_key)
        
        self.rotate_button.setEnabled(keys_match and format_valid)
    
    def rotate_key(self):
        """ביצוע רוטציה"""
        new_key = self.new_key_input.text().strip()
        reason = self.reason_combo.currentText()
        
        # אישור
        reply = QMessageBox.question(
            self, "Confirm Rotation",
            f"Are you sure you want to rotate the API key for {self.provider_name}?\n\n"
            f"Reason: {reason}\n\n"
            "The old key will be deactivated.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.api_key_manager.rotate_api_key(self.provider_name, new_key)
            
            if success:
                QMessageBox.information(self, "Success", "API key rotated successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to rotate API key. Please try again.")
