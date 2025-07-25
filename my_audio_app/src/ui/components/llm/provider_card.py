"""
כרטיס ספק LLM
מציג מידע על ספק LLM עם אפשרויות חיבור, הגדרה ובדיקה
"""

import os
import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QDialog, QProgressBar, QMenu, QToolTip
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QCursor, QAction

# הוספת נתיב למודלים
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from models.llm_models import LLMProvider, ProviderStatus
from services.llm_service import LLMService
from services.api_key_manager import APIKeyManager
from .api_key_dialog import APIKeyDialog


class ConnectionTestWorker(QThread):
    """Worker thread לבדיקת חיבור ברקע"""
    
    test_started = pyqtSignal()
    test_completed = pyqtSignal(bool, str, float)  # success, message, response_time
    test_progress = pyqtSignal(str)  # status message
    
    def __init__(self, llm_service: LLMService, provider_name: str):
        super().__init__()
        self.llm_service = llm_service
        self.provider_name = provider_name
    
    def run(self):
        """ביצוע בדיקת חיבור"""
        self.test_started.emit()
        
        try:
            self.test_progress.emit("מתחבר לספק...")
            success, message, response_time = self.llm_service.test_provider_connection_secure(self.provider_name)
            
            if success:
                self.test_progress.emit("החיבור הצליח!")
            else:
                self.test_progress.emit(f"החיבור נכשל: {message}")
            
            self.test_completed.emit(success, message, response_time)
            
        except Exception as e:
            self.test_completed.emit(False, f"שגיאה בבדיקת חיבור: {str(e)}", 0.0)


class ProviderConfigDialog(QDialog):
    """דיאלוג הגדרות ספק"""
    
    def __init__(self, provider: LLMProvider, parent=None):
        super().__init__(parent)
        self.provider = provider
        
        self.setWindowTitle(f"Provider Configuration - {provider.name}")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # כותרת
        title = QLabel(f"הגדרות {self.provider.name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # מידע על הספק
        info_layout = QVBoxLayout()
        
        # URL בסיס
        url_label = QLabel(f"API Base URL: {self.provider.api_base_url}")
        url_label.setStyleSheet("color: #888; font-size: 12px;")
        info_layout.addWidget(url_label)
        
        # מודלים נתמכים
        models_label = QLabel(f"Supported Models: {', '.join(self.provider.supported_models)}")
        models_label.setStyleSheet("color: #888; font-size: 12px;")
        models_label.setWordWrap(True)
        info_layout.addWidget(models_label)
        
        # מגבלת קצב
        if self.provider.rate_limit:
            rate_label = QLabel(f"Rate Limit: {self.provider.rate_limit} RPM")
            rate_label.setStyleSheet("color: #888; font-size: 12px;")
            info_layout.addWidget(rate_label)
        
        # עלות
        if self.provider.cost_per_1k_tokens:
            cost_label = QLabel(f"Cost per 1K tokens: ${self.provider.cost_per_1k_tokens:.4f}")
            cost_label.setStyleSheet("color: #888; font-size: 12px;")
            info_layout.addWidget(cost_label)
        
        layout.addLayout(info_layout)
        
        # כפתורי פעולה
        buttons_layout = QHBoxLayout()
        
        close_button = QPushButton("סגור")
        close_button.clicked.connect(self.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        # עיצוב
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
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
        """)


class ProviderCard(QFrame):
    """כרטיס ספק LLM עם אינדיקטורי סטטוס ופונקציונליות חיבור"""
    
    # אותות
    connection_changed = pyqtSignal(str, bool)  # provider_name, is_connected
    configuration_requested = pyqtSignal(str)  # provider_name
    test_requested = pyqtSignal(str)  # provider_name
    
    def __init__(self, provider: LLMProvider, llm_service: LLMService, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.llm_service = llm_service
        self.test_worker = None
        
        # הגדרות בסיסיות
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedSize(320, 220)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # הגדרת ממשק המשתמש
        self.setup_ui()
        self.setup_connections()
        self.update_display()
        
        # עיצוב
        self.apply_styling()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # כותרת עם אייקון וסטטוס
        header_layout = QHBoxLayout()
        
        # אייקון ושם ספק
        icon_name_layout = QHBoxLayout()
        
        self.icon_label = QLabel(self.get_provider_icon())
        self.icon_label.setStyleSheet("font-size: 28px;")
        
        self.name_label = QLabel(self.provider.name)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        icon_name_layout.addWidget(self.icon_label)
        icon_name_layout.addWidget(self.name_label)
        icon_name_layout.addStretch()
        
        # סטטוס חיבור
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        header_layout.addLayout(icon_name_layout)
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # מידע על מודלים
        models_layout = QVBoxLayout()
        
        models_title = QLabel("מודלים זמינים:")
        models_title.setStyleSheet("font-weight: bold; font-size: 12px; color: #cccccc; margin-top: 5px;")
        models_layout.addWidget(models_title)
        
        self.models_label = QLabel()
        self.models_label.setWordWrap(True)
        self.models_label.setStyleSheet("color: #888888; font-size: 11px; margin-bottom: 5px;")
        models_layout.addWidget(self.models_label)
        
        layout.addLayout(models_layout)
        
        # מידע נוסף (עלות ומגבלות)
        info_layout = QHBoxLayout()
        
        self.cost_label = QLabel()
        self.cost_label.setStyleSheet("color: #888888; font-size: 10px;")
        
        self.rate_label = QLabel()
        self.rate_label.setStyleSheet("color: #888888; font-size: 10px;")
        
        info_layout.addWidget(self.cost_label)
        info_layout.addStretch()
        info_layout.addWidget(self.rate_label)
        
        layout.addLayout(info_layout)
        
        # פס התקדמות לבדיקת חיבור
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # הודעת סטטוס
        self.status_message = QLabel()
        self.status_message.setVisible(False)
        self.status_message.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        self.status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_message)
        
        layout.addStretch()
        
        # כפתורי פעולה
        buttons_layout = QHBoxLayout()
        
        # כפתור ראשי (חיבור/הגדרה)
        self.primary_button = QPushButton()
        self.primary_button.setFixedHeight(32)
        
        # כפתור בדיקה
        self.test_button = QPushButton("🧪 Test")
        self.test_button.setFixedHeight(32)
        self.test_button.setFixedWidth(70)
        
        # כפתור תפריט
        self.menu_button = QPushButton("⋮")
        self.menu_button.setFixedSize(32, 32)
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """)
        
        buttons_layout.addWidget(self.primary_button)
        buttons_layout.addWidget(self.test_button)
        buttons_layout.addWidget(self.menu_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """הגדרת חיבורים לאותות"""
        self.primary_button.clicked.connect(self.on_primary_action)
        self.test_button.clicked.connect(self.test_connection)
        self.menu_button.clicked.connect(self.show_context_menu)
        
        # חיבור לאותות של שירות LLM
        self.llm_service.provider_connected.connect(self.on_provider_connected)
        self.llm_service.provider_disconnected.connect(self.on_provider_disconnected)
    
    def get_provider_icon(self) -> str:
        """קבלת אייקון לפי ספק"""
        icons = {
            "OpenAI": "🤖",
            "Anthropic": "🧠", 
            "Google": "🔍",
            "Cohere": "💬",
            "Hugging Face": "🤗"
        }
        return icons.get(self.provider.name, "🔧")
    
    def update_display(self):
        """עדכון תצוגת הכרטיס"""
        # עדכון סטטוס
        self.update_status_display()
        
        # עדכון מודלים
        models_text = ", ".join(self.provider.supported_models[:3])  # הצגת 3 ראשונים
        if len(self.provider.supported_models) > 3:
            models_text += f" ועוד {len(self.provider.supported_models) - 3}"
        self.models_label.setText(models_text)
        
        # עדכון מידע נוסף
        if self.provider.cost_per_1k_tokens:
            self.cost_label.setText(f"${self.provider.cost_per_1k_tokens:.4f}/1K tokens")
        else:
            self.cost_label.setText("")
        
        if self.provider.rate_limit:
            self.rate_label.setText(f"{self.provider.rate_limit} RPM")
        else:
            self.rate_label.setText("")
        
        # עדכון כפתור ראשי
        self.update_primary_button()
        
        # עדכון כפתור בדיקה
        self.test_button.setEnabled(self.provider.connection_status != ProviderStatus.TESTING)
    
    def update_status_display(self):
        """עדכון תצוגת סטטוס"""
        status_styles = {
            ProviderStatus.CONNECTED: {
                "text": "🟢 מחובר",
                "color": "#4CAF50",
                "tooltip": f"מחובר בהצלחה. בדיקה אחרונה: {self.provider.last_test_date.strftime('%H:%M') if self.provider.last_test_date else 'לא ידוע'}"
            },
            ProviderStatus.DISCONNECTED: {
                "text": "🔴 מנותק", 
                "color": "#F44336",
                "tooltip": "לא מחובר. נדרש מפתח API או הגדרה"
            },
            ProviderStatus.TESTING: {
                "text": "🟡 בודק...",
                "color": "#FF9800", 
                "tooltip": "בודק חיבור לספק"
            },
            ProviderStatus.ERROR: {
                "text": "❌ שגיאה",
                "color": "#F44336",
                "tooltip": f"שגיאה בחיבור: {self.provider.error_message or 'לא ידוע'}"
            }
        }
        
        status_info = status_styles.get(self.provider.connection_status, status_styles[ProviderStatus.DISCONNECTED])
        
        self.status_label.setText(status_info["text"])
        self.status_label.setStyleSheet(f"color: {status_info['color']}; font-size: 12px; font-weight: bold;")
        self.status_label.setToolTip(status_info["tooltip"])
    
    def update_primary_button(self):
        """עדכון כפתור ראשי"""
        if self.provider.connection_status == ProviderStatus.CONNECTED:
            self.primary_button.setText("⚙️ הגדרות")
            self.primary_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
        else:
            self.primary_button.setText("🔗 חיבור")
            self.primary_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #2E7D32;
                }
            """)
    
    def on_primary_action(self):
        """טיפול בלחיצה על כפתור ראשי"""
        if self.provider.connection_status == ProviderStatus.CONNECTED:
            self.configure_provider()
        else:
            self.connect_provider()
    
    def connect_provider(self):
        """חיבור לספק"""
        try:
            # פתיחת דיאלוג מפתח API
            dialog = APIKeyDialog(self.provider.name, self.llm_service.api_key_manager, self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                api_key = dialog.get_api_key()
                if api_key:
                    # שמירת מפתח API
                    success = self.llm_service.set_provider_api_key(self.provider.name, api_key)
                    
                    if success:
                        # עדכון הספק
                        self.provider.api_key = api_key
                        self.provider.connection_status = ProviderStatus.DISCONNECTED
                        
                        # בדיקת חיבור אוטומטית
                        QTimer.singleShot(500, self.test_connection)
                        
                        QMessageBox.information(self, "הצלחה", "מפתח API נשמר בהצלחה!")
                    else:
                        QMessageBox.critical(self, "שגיאה", "שמירת מפתח API נכשלה.")
        
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בחיבור לספק: {str(e)}")
    
    def configure_provider(self):
        """הגדרת ספק"""
        try:
            dialog = ProviderConfigDialog(self.provider, self)
            dialog.exec()
            self.configuration_requested.emit(self.provider.name)
        
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בהגדרת ספק: {str(e)}")
    
    def test_connection(self):
        """בדיקת חיבור לספק"""
        if not self.provider.api_key and not self.llm_service.get_provider_api_key(self.provider.name):
            QMessageBox.warning(self, "אזהרה", "נדרש מפתח API לבדיקת חיבור.")
            self.connect_provider()
            return
        
        try:
            # עדכון סטטוס לבדיקה
            self.provider.connection_status = ProviderStatus.TESTING
            self.update_display()
            
            # הצגת פס התקדמות
            self.show_progress("מתחיל בדיקת חיבור...")
            
            # הרצת בדיקה ברקע
            self.test_worker = ConnectionTestWorker(self.llm_service, self.provider.name)
            self.test_worker.test_started.connect(self.on_test_started)
            self.test_worker.test_progress.connect(self.on_test_progress)
            self.test_worker.test_completed.connect(self.on_test_completed)
            self.test_worker.start()
            
            self.test_requested.emit(self.provider.name)
        
        except Exception as e:
            self.hide_progress()
            self.provider.connection_status = ProviderStatus.ERROR
            self.provider.error_message = str(e)
            self.update_display()
            QMessageBox.critical(self, "שגיאה", f"שגיאה בבדיקת חיבור: {str(e)}")
    
    def show_context_menu(self):
        """הצגת תפריט הקשר"""
        menu = QMenu(self)
        
        # פעולות בסיסיות
        if self.provider.connection_status == ProviderStatus.CONNECTED:
            configure_action = QAction("⚙️ הגדרות", self)
            configure_action.triggered.connect(self.configure_provider)
            menu.addAction(configure_action)
            
            disconnect_action = QAction("🔌 ניתוק", self)
            disconnect_action.triggered.connect(self.disconnect_provider)
            menu.addAction(disconnect_action)
        else:
            connect_action = QAction("🔗 חיבור", self)
            connect_action.triggered.connect(self.connect_provider)
            menu.addAction(connect_action)
        
        menu.addSeparator()
        
        # בדיקת חיבור
        test_action = QAction("🧪 בדיקת חיבור", self)
        test_action.triggered.connect(self.test_connection)
        test_action.setEnabled(self.provider.connection_status != ProviderStatus.TESTING)
        menu.addAction(test_action)
        
        # רענון
        refresh_action = QAction("🔄 רענון", self)
        refresh_action.triggered.connect(self.refresh_provider_data)
        menu.addAction(refresh_action)
        
        menu.addSeparator()
        
        # מידע
        info_action = QAction("ℹ️ מידע", self)
        info_action.triggered.connect(self.show_provider_info)
        menu.addAction(info_action)
        
        # הצגת התפריט
        menu.exec(QCursor.pos())
    
    def disconnect_provider(self):
        """ניתוק מהספק"""
        reply = QMessageBox.question(
            self, "אישור ניתוק",
            f"האם אתה בטוח שברצונך להתנתק מ-{self.provider.name}?\n\n"
            "מפתח ה-API יישאר שמור אך החיבור יתנתק.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.provider.disconnect()
            self.llm_service.save_provider(self.provider)
            self.update_display()
            self.connection_changed.emit(self.provider.name, False)
            QMessageBox.information(self, "הצלחה", f"התנתקת בהצלחה מ-{self.provider.name}")
    
    def refresh_provider_data(self):
        """רענון נתוני ספק"""
        try:
            # טעינת נתונים מחדש מהשירות
            updated_provider = self.llm_service.get_provider(self.provider.name)
            if updated_provider:
                self.provider = updated_provider
                self.update_display()
                QMessageBox.information(self, "רענון", "נתוני הספק עודכנו בהצלחה")
            else:
                QMessageBox.warning(self, "שגיאה", "לא ניתן לטעון נתוני ספק")
        
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה ברענון נתונים: {str(e)}")
    
    def show_provider_info(self):
        """הצגת מידע על הספק"""
        info_text = f"""
        <h3>{self.provider.name}</h3>
        <p><b>API Base URL:</b> {self.provider.api_base_url}</p>
        <p><b>מודלים נתמכים:</b> {', '.join(self.provider.supported_models)}</p>
        <p><b>סטטוס:</b> {self.provider.status_display}</p>
        """
        
        if self.provider.rate_limit:
            info_text += f"<p><b>מגבלת קצב:</b> {self.provider.rate_limit} בקשות לדקה</p>"
        
        if self.provider.cost_per_1k_tokens:
            info_text += f"<p><b>עלות:</b> ${self.provider.cost_per_1k_tokens:.4f} לאלף טוקנים</p>"
        
        if self.provider.last_test_date:
            info_text += f"<p><b>בדיקה אחרונה:</b> {self.provider.last_test_date.strftime('%d/%m/%Y %H:%M')}</p>"
        
        if self.provider.error_message:
            info_text += f"<p><b>שגיאה אחרונה:</b> {self.provider.error_message}</p>"
        
        QMessageBox.information(self, f"מידע על {self.provider.name}", info_text)
    
    def show_progress(self, message: str):
        """הצגת פס התקדמות"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # אינסופי
        self.status_message.setText(message)
        self.status_message.setVisible(True)
        
        # השבתת כפתורים
        self.primary_button.setEnabled(False)
        self.test_button.setEnabled(False)
    
    def hide_progress(self):
        """הסתרת פס התקדמות"""
        self.progress_bar.setVisible(False)
        self.status_message.setVisible(False)
        
        # הפעלת כפתורים
        self.primary_button.setEnabled(True)
        self.test_button.setEnabled(True)
    
    def on_test_started(self):
        """טיפול בתחילת בדיקה"""
        self.show_progress("בודק חיבור...")
    
    def on_test_progress(self, message: str):
        """טיפול בהתקדמות בדיקה"""
        self.status_message.setText(message)
    
    def on_test_completed(self, success: bool, message: str, response_time: float):
        """טיפול בסיום בדיקת חיבור"""
        self.hide_progress()
        
        # עדכון סטטוס הספק
        if success:
            self.provider.connection_status = ProviderStatus.CONNECTED
            self.provider.is_connected = True
            self.provider.error_message = None
            self.provider.last_test_date = self.llm_service.get_provider(self.provider.name).last_test_date
        else:
            self.provider.connection_status = ProviderStatus.ERROR
            self.provider.is_connected = False
            self.provider.error_message = message
        
        # עדכון תצוגה
        self.update_display()
        
        # שליחת אות
        self.connection_changed.emit(self.provider.name, success)
        
        # הודעה למשתמש
        if success:
            time_str = f"{response_time:.2f}s" if response_time > 0 else "N/A"
            QMessageBox.information(
                self, "בדיקת חיבור הצליחה",
                f"החיבור ל-{self.provider.name} הצליח!\n\nזמן תגובה: {time_str}"
            )
        else:
            QMessageBox.warning(
                self, "בדיקת חיבור נכשלה",
                f"החיבור ל-{self.provider.name} נכשל:\n\n{message}"
            )
    
    def on_provider_connected(self, provider_name: str):
        """טיפול בחיבור ספק"""
        if provider_name == self.provider.name:
            # רענון נתוני ספק
            updated_provider = self.llm_service.get_provider(provider_name)
            if updated_provider:
                self.provider = updated_provider
                self.update_display()
    
    def on_provider_disconnected(self, provider_name: str):
        """טיפול בניתוק ספק"""
        if provider_name == self.provider.name:
            # רענון נתוני ספק
            updated_provider = self.llm_service.get_provider(provider_name)
            if updated_provider:
                self.provider = updated_provider
                self.update_display()
    
    def apply_styling(self):
        """החלת עיצוב על הכרטיס"""
        self.setStyleSheet("""
            ProviderCard {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
            }
            ProviderCard:hover {
                border-color: #555;
                background-color: #252525;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
        """)
    
    def enterEvent(self, event):
        """אירוע כניסה לכרטיס"""
        self.setStyleSheet(self.styleSheet().replace("border-color: #333", "border-color: #555"))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """אירוע יציאה מהכרטיס"""
        self.setStyleSheet(self.styleSheet().replace("border-color: #555", "border-color: #333"))
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """אירוע לחיצת עכבר"""
        if event.button() == Qt.MouseButton.LeftButton:
            # לחיצה שמאלית - פעולה ראשית
            self.on_primary_action()
        elif event.button() == Qt.MouseButton.RightButton:
            # לחיצה ימנית - תפריט הקשר
            self.show_context_menu()
        
        super().mousePressEvent(event)
    
    def update_provider_data(self, provider: LLMProvider):
        """עדכון נתוני ספק"""
        self.provider = provider
        self.update_display()