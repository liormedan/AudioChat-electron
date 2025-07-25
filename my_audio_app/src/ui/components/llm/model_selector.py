"""
רכיב בחירת מודלי LLM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QListWidget, QListWidgetItem, QPushButton, QFrame,
    QGroupBox, QCheckBox, QLineEdit, QScrollArea,
    QSizePolicy, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor

from models.llm_models import LLMModel, LLMProvider, ModelCapability
from services.llm_service import LLMService


class ModelAvailabilityChecker(QThread):
    """בודק זמינות מודלים ברקע"""
    
    availability_checked = pyqtSignal(str, bool)  # model_id, is_available
    
    def __init__(self, llm_service: LLMService, model_ids: list):
        super().__init__()
        self.llm_service = llm_service
        self.model_ids = model_ids
        self.running = True
    
    def run(self):
        """בדיקת זמינות מודלים"""
        for model_id in self.model_ids:
            if not self.running:
                break
            
            # כאן תהיה בדיקת זמינות אמיתית
            # לעת עתה נחזיר True לכל המודלים
            is_available = True
            
            self.availability_checked.emit(model_id, is_available)
            self.msleep(100)  # השהיה קצרה
    
    def stop(self):
        """עצירת הבדיקה"""
        self.running = False


class ModelListItem(QFrame):
    """פריט במודל ברשימה"""
    
    model_selected = pyqtSignal(str)  # model_id
    model_activated = pyqtSignal(str)  # model_id
    
    def __init__(self, model: LLMModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedHeight(80)
        
        # לייאאוט
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # מידע מודל
        info_layout = QVBoxLayout()
        
        # שם מודל
        name_layout = QHBoxLayout()
        
        self.name_label = QLabel(model.name)
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        name_layout.addWidget(self.name_label)
        
        # אינדיקטור מודל פעיל
        if model.is_active:
            active_label = QLabel("🟢 פעיל")
            active_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
            name_layout.addWidget(active_label)
        
        name_layout.addStretch()
        
        # סטטוס זמינות
        self.availability_label = QLabel("🟡 בודק...")
        self.availability_label.setStyleSheet("font-size: 12px;")
        name_layout.addWidget(self.availability_label)
        
        info_layout.addLayout(name_layout)
        
        # תיאור
        desc_label = QLabel(model.description[:60] + "..." if len(model.description) > 60 else model.description)
        desc_label.setStyleSheet("color: #888; font-size: 11px;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        # מידע נוסף
        details_layout = QHBoxLayout()
        
        provider_label = QLabel(f"ספק: {model.provider}")
        provider_label.setStyleSheet("color: #666; font-size: 10px;")
        details_layout.addWidget(provider_label)
        
        cost_label = QLabel(f"עלות: ${model.cost_per_1k_tokens:.4f}/1K")
        cost_label.setStyleSheet("color: #666; font-size: 10px;")
        details_layout.addWidget(cost_label)
        
        tokens_label = QLabel(f"טוקנים: {model.max_tokens:,}")
        tokens_label.setStyleSheet("color: #666; font-size: 10px;")
        details_layout.addWidget(tokens_label)
        
        details_layout.addStretch()
        
        info_layout.addLayout(details_layout)
        
        layout.addLayout(info_layout, 1)
        
        # כפתורי פעולה
        actions_layout = QVBoxLayout()
        
        self.select_button = QPushButton("בחר")
        self.select_button.setFixedSize(60, 25)
        self.select_button.clicked.connect(self.on_select_clicked)
        
        self.activate_button = QPushButton("הפעל")
        self.activate_button.setFixedSize(60, 25)
        self.activate_button.clicked.connect(self.on_activate_clicked)
        self.activate_button.setEnabled(not model.is_active)
        
        actions_layout.addWidget(self.select_button)
        actions_layout.addWidget(self.activate_button)
        
        layout.addLayout(actions_layout)
        
        # עיצוב
        self.setStyleSheet("""
            ModelListItem {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
                margin: 2px;
            }
            ModelListItem:hover {
                border-color: #666;
                background-color: #333;
            }
        """)
    
    def on_select_clicked(self):
        """טיפול בלחיצה על בחירה"""
        self.model_selected.emit(self.model.id)
    
    def on_activate_clicked(self):
        """טיפול בלחיצה על הפעלה"""
        self.model_activated.emit(self.model.id)
    
    def update_availability(self, is_available: bool):
        """עדכון סטטוס זמינות"""
        if is_available:
            self.availability_label.setText("🟢 זמין")
            self.availability_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
            self.select_button.setEnabled(True)
            self.activate_button.setEnabled(not self.model.is_active)
        else:
            self.availability_label.setText("🔴 לא זמין")
            self.availability_label.setStyleSheet("color: #F44336; font-size: 12px;")
            self.select_button.setEnabled(False)
            self.activate_button.setEnabled(False)
    
    def set_active(self, is_active: bool):
        """הגדרת מצב פעיל"""
        self.model.is_active = is_active
        self.activate_button.setEnabled(not is_active)
        
        # עדכון תצוגה
        if is_active:
            if not self.name_label.text().endswith(" (פעיל)"):
                self.name_label.setText(f"{self.model.name} (פעיל)")
                self.name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        else:
            self.name_label.setText(self.model.name)
            self.name_label.setStyleSheet("font-size: 14px; font-weight: bold;")


class ModelSelector(QWidget):
    """רכיב בחירת מודלי LLM"""
    
    model_selected = pyqtSignal(str)  # model_id
    model_activated = pyqtSignal(str)  # model_id
    
    def __init__(self, llm_service: LLMService, parent=None):
        super().__init__(parent)
        self.llm_service = llm_service
        self.model_items = {}  # model_id -> ModelListItem
        self.availability_checker = None
        
        self.setup_ui()
        self.connect_signals()
        self.load_models()
        self.start_availability_check()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # כותרת
        title = QLabel("בחירת מודל LLM")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # פילטרים
        filters_group = QGroupBox("פילטרים")
        filters_layout = QVBoxLayout(filters_group)
        
        # פילטר ספק
        provider_layout = QHBoxLayout()
        provider_label = QLabel("ספק:")
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("כל הספקים", "all")
        self.provider_combo.currentTextChanged.connect(self.filter_models)
        
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        
        filters_layout.addLayout(provider_layout)
        
        # פילטר יכולות
        capabilities_layout = QHBoxLayout()
        capabilities_label = QLabel("יכולות:")
        
        self.text_gen_check = QCheckBox("יצירת טקסט")
        self.chat_check = QCheckBox("שיחה")
        self.code_check = QCheckBox("קוד")
        self.audio_check = QCheckBox("אודיו")
        
        self.text_gen_check.stateChanged.connect(self.filter_models)
        self.chat_check.stateChanged.connect(self.filter_models)
        self.code_check.stateChanged.connect(self.filter_models)
        self.audio_check.stateChanged.connect(self.filter_models)
        
        capabilities_layout.addWidget(capabilities_label)
        capabilities_layout.addWidget(self.text_gen_check)
        capabilities_layout.addWidget(self.chat_check)
        capabilities_layout.addWidget(self.code_check)
        capabilities_layout.addWidget(self.audio_check)
        capabilities_layout.addStretch()
        
        filters_layout.addLayout(capabilities_layout)
        
        # חיפוש
        search_layout = QHBoxLayout()
        search_label = QLabel("חיפוש:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("חפש מודל...")
        self.search_input.textChanged.connect(self.filter_models)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        filters_layout.addLayout(search_layout)
        
        layout.addWidget(filters_group)
        
        # רשימת מודלים
        models_group = QGroupBox("מודלים זמינים")
        models_layout = QVBoxLayout(models_group)
        
        # אזור גלילה
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # רכיב רשימה
        self.models_widget = QWidget()
        self.models_layout = QVBoxLayout(self.models_widget)
        self.models_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.models_widget)
        models_layout.addWidget(scroll_area)
        
        layout.addWidget(models_group)
        
        # סטטוס
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("טוען מודלים...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
    
    def connect_signals(self):
        """חיבור אותות"""
        self.llm_service.model_activated.connect(self.on_model_activated)
    
    def load_models(self):
        """טעינת מודלים"""
        try:
            # טעינת ספקים לפילטר
            providers = self.llm_service.get_all_providers()
            for provider in providers:
                self.provider_combo.addItem(provider.name, provider.name)
            
            # טעינת מודלים
            models = self.llm_service.get_all_models()
            
            # ניקוי רשימה קיימת
            self.clear_models_list()
            
            # יצירת פריטי מודל
            for model in models:
                model_item = ModelListItem(model)
                model_item.model_selected.connect(self.on_model_item_selected)
                model_item.model_activated.connect(self.on_model_item_activated)
                
                self.models_layout.addWidget(model_item)
                self.model_items[model.id] = model_item
            
            self.status_label.setText(f"נטענו {len(models)} מודלים")
            
        except Exception as e:
            self.status_label.setText(f"שגיאה בטעינת מודלים: {str(e)}")
            QMessageBox.warning(self, "שגיאה", f"לא ניתן לטעון מודלים:\n{str(e)}")
    
    def clear_models_list(self):
        """ניקוי רשימת מודלים"""
        for model_item in self.model_items.values():
            model_item.setParent(None)
            model_item.deleteLater()
        
        self.model_items.clear()
    
    def filter_models(self):
        """פילטור מודלים"""
        provider_filter = self.provider_combo.currentData()
        search_text = self.search_input.text().lower()
        
        # יכולות נבחרות
        selected_capabilities = []
        if self.text_gen_check.isChecked():
            selected_capabilities.append(ModelCapability.TEXT_GENERATION)
        if self.chat_check.isChecked():
            selected_capabilities.append(ModelCapability.CHAT)
        if self.code_check.isChecked():
            selected_capabilities.append(ModelCapability.CODE_GENERATION)
        if self.audio_check.isChecked():
            selected_capabilities.extend([
                ModelCapability.AUDIO_TRANSCRIPTION,
                ModelCapability.AUDIO_ANALYSIS
            ])
        
        visible_count = 0
        
        for model_id, model_item in self.model_items.items():
            model = model_item.model
            
            # בדיקת פילטר ספק
            if provider_filter != "all" and model.provider != provider_filter:
                model_item.setVisible(False)
                continue
            
            # בדיקת חיפוש
            if search_text and search_text not in model.name.lower() and search_text not in model.description.lower():
                model_item.setVisible(False)
                continue
            
            # בדיקת יכולות
            if selected_capabilities:
                has_capability = any(cap in model.capabilities for cap in selected_capabilities)
                if not has_capability:
                    model_item.setVisible(False)
                    continue
            
            model_item.setVisible(True)
            visible_count += 1
        
        self.status_label.setText(f"מוצגים {visible_count} מודלים")
    
    def start_availability_check(self):
        """התחלת בדיקת זמינות"""
        if self.availability_checker and self.availability_checker.isRunning():
            self.availability_checker.stop()
            self.availability_checker.wait()
        
        model_ids = list(self.model_items.keys())
        if model_ids:
            self.availability_checker = ModelAvailabilityChecker(self.llm_service, model_ids)
            self.availability_checker.availability_checked.connect(self.on_availability_checked)
            self.availability_checker.start()
    
    @pyqtSlot(str, bool)
    def on_availability_checked(self, model_id: str, is_available: bool):
        """טיפול בתוצאת בדיקת זמינות"""
        if model_id in self.model_items:
            self.model_items[model_id].update_availability(is_available)
    
    def on_model_item_selected(self, model_id: str):
        """טיפול בבחירת מודל"""
        self.model_selected.emit(model_id)
    
    def on_model_item_activated(self, model_id: str):
        """טיפול בהפעלת מודל"""
        try:
            success = self.llm_service.set_active_model(model_id)
            if success:
                self.status_label.setText(f"מודל {model_id} הופעל בהצלחה")
            else:
                QMessageBox.warning(self, "שגיאה", "לא ניתן להפעיל את המודל")
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בהפעלת מודל:\n{str(e)}")
    
    @pyqtSlot(str)
    def on_model_activated(self, model_id: str):
        """טיפול באות הפעלת מודל"""
        # עדכון כל הפריטים
        for mid, model_item in self.model_items.items():
            model_item.set_active(mid == model_id)
    
    def refresh_models(self):
        """רענון רשימת מודלים"""
        self.load_models()
        self.start_availability_check()
    
    def get_selected_model_id(self) -> str:
        """קבלת ID של המודל הנבחר"""
        active_model = self.llm_service.get_active_model()
        return active_model.id if active_model else None
    
    def closeEvent(self, event):
        """סגירת הרכיב"""
        if self.availability_checker and self.availability_checker.isRunning():
            self.availability_checker.stop()
            self.availability_checker.wait()
        
        super().closeEvent(event)