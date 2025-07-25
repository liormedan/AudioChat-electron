"""
רכיב הצגת פרטי מודל LLM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGroupBox, QScrollArea, QTextEdit, QPushButton,
    QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QTabWidget, QGridLayout,
    QMessageBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter

from models.llm_models import LLMModel, ModelCapability
from services.llm_service import LLMService


class ModelComparisonDialog(QDialog):
    """דיאלוג השוואת מודלים"""
    
    def __init__(self, models: list, parent=None):
        super().__init__(parent)
        self.models = models
        self.setWindowTitle("השוואת מודלים")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # כותרת
        title = QLabel("השוואת מודלים")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # טבלת השוואה
        self.comparison_table = QTableWidget()
        self.setup_comparison_table()
        layout.addWidget(self.comparison_table)
        
        # כפתורים
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def setup_comparison_table(self):
        """הגדרת טבלת השוואה"""
        if not self.models:
            return
        
        # הגדרת עמודות
        self.comparison_table.setColumnCount(len(self.models))
        self.comparison_table.setHorizontalHeaderLabels([model.name for model in self.models])
        
        # שורות להשוואה
        comparison_rows = [
            ("ספק", lambda m: m.provider),
            ("תיאור", lambda m: m.description[:50] + "..." if len(m.description) > 50 else m.description),
            ("מקסימום טוקנים", lambda m: f"{m.max_tokens:,}"),
            ("חלון הקשר", lambda m: f"{m.context_window:,}"),
            ("עלות לאלף טוקנים", lambda m: f"${m.cost_per_1k_tokens:.4f}"),
            ("יכולות", lambda m: m.capabilities_display),
            ("גרסה", lambda m: m.version or "לא צוין"),
            ("זמין", lambda m: "✅ כן" if m.is_available else "❌ לא"),
            ("פעיל", lambda m: "🟢 כן" if m.is_active else "⚪ לא")
        ]
        
        self.comparison_table.setRowCount(len(comparison_rows))
        self.comparison_table.setVerticalHeaderLabels([row[0] for row in comparison_rows])
        
        # מילוי נתונים
        for row_idx, (_, value_func) in enumerate(comparison_rows):
            for col_idx, model in enumerate(self.models):
                try:
                    value = value_func(model)
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.comparison_table.setItem(row_idx, col_idx, item)
                except Exception as e:
                    item = QTableWidgetItem("שגיאה")
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.comparison_table.setItem(row_idx, col_idx, item)
        
        # התאמת רוחב עמודות
        header = self.comparison_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


class ModelPerformanceWidget(QWidget):
    """רכיב הצגת ביצועי מודל"""
    
    def __init__(self, model: LLMModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setup_ui()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # מטריקות ביצועים
        metrics_group = QGroupBox("מטריקות ביצועים")
        metrics_layout = QGridLayout(metrics_group)
        
        # זמן תגובה ממוצע
        response_time_label = QLabel("זמן תגובה ממוצע:")
        self.response_time_value = QLabel("טוען...")
        metrics_layout.addWidget(response_time_label, 0, 0)
        metrics_layout.addWidget(self.response_time_value, 0, 1)
        
        # אחוז הצלחה
        success_rate_label = QLabel("אחוז הצלחה:")
        self.success_rate_value = QLabel("טוען...")
        metrics_layout.addWidget(success_rate_label, 1, 0)
        metrics_layout.addWidget(self.success_rate_value, 1, 1)
        
        # שימוש חודשי
        monthly_usage_label = QLabel("שימוש חודשי:")
        self.monthly_usage_value = QLabel("טוען...")
        metrics_layout.addWidget(monthly_usage_label, 2, 0)
        metrics_layout.addWidget(self.monthly_usage_value, 2, 1)
        
        # עלות חודשית
        monthly_cost_label = QLabel("עלות חודשית:")
        self.monthly_cost_value = QLabel("טוען...")
        metrics_layout.addWidget(monthly_cost_label, 3, 0)
        metrics_layout.addWidget(self.monthly_cost_value, 3, 1)
        
        layout.addWidget(metrics_group)
        
        # גרף ביצועים (placeholder)
        chart_group = QGroupBox("גרף ביצועים")
        chart_layout = QVBoxLayout(chart_group)
        
        chart_placeholder = QLabel("📊 גרף ביצועים יוצג כאן")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("""
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 40px;
            color: #888;
        """)
        chart_layout.addWidget(chart_placeholder)
        
        layout.addWidget(chart_group)
        
        # טעינת נתונים
        self.load_performance_data()
    
    def load_performance_data(self):
        """טעינת נתוני ביצועים"""
        # כאן תהיה טעינת נתונים אמיתית
        # לעת עתה נציג נתונים דמה
        QTimer.singleShot(1000, self.update_performance_data)
    
    def update_performance_data(self):
        """עדכון נתוני ביצועים"""
        # נתונים דמה
        self.response_time_value.setText("1.2 שניות")
        self.success_rate_value.setText("98.5%")
        self.monthly_usage_value.setText("15,234 טוקנים")
        self.monthly_cost_value.setText("$4.57")


class ModelDetailsWidget(QWidget):
    """רכיב הצגת פרטי מודל מפורטים"""
    
    model_activated = pyqtSignal(str)  # model_id
    compare_requested = pyqtSignal(list)  # list of model_ids
    
    def __init__(self, llm_service: LLMService, parent=None):
        super().__init__(parent)
        self.llm_service = llm_service
        self.current_model = None
        self.comparison_models = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # כותרת
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("פרטי מודל")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # כפתורי פעולה
        self.activate_button = QPushButton("הפעל מודל")
        self.activate_button.clicked.connect(self.activate_model)
        self.activate_button.setEnabled(False)
        
        self.compare_button = QPushButton("השווה מודלים")
        self.compare_button.clicked.connect(self.show_comparison)
        self.compare_button.setEnabled(False)
        
        header_layout.addWidget(self.activate_button)
        header_layout.addWidget(self.compare_button)
        
        layout.addLayout(header_layout)
        
        # תוכן ראשי
        self.content_widget = QTabWidget()
        
        # טאב מידע כללי
        self.info_tab = self.create_info_tab()
        self.content_widget.addTab(self.info_tab, "מידע כללי")
        
        # טאב ביצועים
        self.performance_tab = QWidget()
        self.content_widget.addTab(self.performance_tab, "ביצועים")
        
        # טאב הגדרות
        self.settings_tab = self.create_settings_tab()
        self.content_widget.addTab(self.settings_tab, "הגדרות")
        
        layout.addWidget(self.content_widget)
        
        # הודעת ברירת מחדל
        self.show_empty_state()
    
    def create_info_tab(self) -> QWidget:
        """יצירת טאב מידע כללי"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # מידע בסיסי
        basic_group = QGroupBox("מידע בסיסי")
        basic_layout = QGridLayout(basic_group)
        
        # שם מודל
        basic_layout.addWidget(QLabel("שם:"), 0, 0)
        self.name_value = QLabel("-")
        self.name_value.setStyleSheet("font-weight: bold;")
        basic_layout.addWidget(self.name_value, 0, 1)
        
        # ספק
        basic_layout.addWidget(QLabel("ספק:"), 1, 0)
        self.provider_value = QLabel("-")
        basic_layout.addWidget(self.provider_value, 1, 1)
        
        # גרסה
        basic_layout.addWidget(QLabel("גרסה:"), 2, 0)
        self.version_value = QLabel("-")
        basic_layout.addWidget(self.version_value, 2, 1)
        
        # סטטוס
        basic_layout.addWidget(QLabel("סטטוס:"), 3, 0)
        self.status_value = QLabel("-")
        basic_layout.addWidget(self.status_value, 3, 1)
        
        layout.addWidget(basic_group)
        
        # תיאור
        desc_group = QGroupBox("תיאור")
        desc_layout = QVBoxLayout(desc_group)
        
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        desc_layout.addWidget(self.description_text)
        
        layout.addWidget(desc_group)
        
        # מפרטים טכניים
        specs_group = QGroupBox("מפרטים טכניים")
        specs_layout = QGridLayout(specs_group)
        
        # מקסימום טוקנים
        specs_layout.addWidget(QLabel("מקסימום טוקנים:"), 0, 0)
        self.max_tokens_value = QLabel("-")
        specs_layout.addWidget(self.max_tokens_value, 0, 1)
        
        # חלון הקשר
        specs_layout.addWidget(QLabel("חלון הקשר:"), 1, 0)
        self.context_window_value = QLabel("-")
        specs_layout.addWidget(self.context_window_value, 1, 1)
        
        # עלות לטוקן
        specs_layout.addWidget(QLabel("עלות לטוקן:"), 2, 0)
        self.cost_per_token_value = QLabel("-")
        specs_layout.addWidget(self.cost_per_token_value, 2, 1)
        
        # עלות לאלף טוקנים
        specs_layout.addWidget(QLabel("עלות לאלף טוקנים:"), 3, 0)
        self.cost_per_1k_value = QLabel("-")
        specs_layout.addWidget(self.cost_per_1k_value, 3, 1)
        
        layout.addWidget(specs_group)
        
        # יכולות
        capabilities_group = QGroupBox("יכולות")
        capabilities_layout = QVBoxLayout(capabilities_group)
        
        self.capabilities_text = QTextEdit()
        self.capabilities_text.setReadOnly(True)
        self.capabilities_text.setMaximumHeight(80)
        capabilities_layout.addWidget(self.capabilities_text)
        
        layout.addWidget(capabilities_group)
        
        layout.addStretch()
        
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """יצירת טאב הגדרות"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # הגדרות מודל
        settings_group = QGroupBox("הגדרות מודל")
        settings_layout = QGridLayout(settings_group)
        
        # זמינות
        settings_layout.addWidget(QLabel("זמין:"), 0, 0)
        self.availability_value = QLabel("-")
        settings_layout.addWidget(self.availability_value, 0, 1)
        
        # תאריך עדכון אחרון
        settings_layout.addWidget(QLabel("עדכון אחרון:"), 1, 0)
        self.last_update_value = QLabel("-")
        settings_layout.addWidget(self.last_update_value, 1, 1)
        
        # נתוני אימון
        settings_layout.addWidget(QLabel("נתוני אימון עד:"), 2, 0)
        self.training_cutoff_value = QLabel("-")
        settings_layout.addWidget(self.training_cutoff_value, 2, 1)
        
        layout.addWidget(settings_group)
        
        # מטא-נתונים
        metadata_group = QGroupBox("מטא-נתונים")
        metadata_layout = QVBoxLayout(metadata_group)
        
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(150)
        metadata_layout.addWidget(self.metadata_text)
        
        layout.addWidget(metadata_group)
        
        layout.addStretch()
        
        return widget
    
    def show_empty_state(self):
        """הצגת מצב ריק"""
        self.title_label.setText("בחר מודל לצפייה בפרטים")
        self.activate_button.setEnabled(False)
        self.compare_button.setEnabled(False)
        
        # איפוס כל השדות
        self.name_value.setText("-")
        self.provider_value.setText("-")
        self.version_value.setText("-")
        self.status_value.setText("-")
        self.description_text.setPlainText("")
        self.max_tokens_value.setText("-")
        self.context_window_value.setText("-")
        self.cost_per_token_value.setText("-")
        self.cost_per_1k_value.setText("-")
        self.capabilities_text.setPlainText("")
        self.availability_value.setText("-")
        self.last_update_value.setText("-")
        self.training_cutoff_value.setText("-")
        self.metadata_text.setPlainText("")
    
    def show_model_details(self, model_id: str):
        """הצגת פרטי מודל"""
        try:
            model = self.llm_service.get_model(model_id)
            if not model:
                self.show_empty_state()
                return
            
            self.current_model = model
            
            # עדכון כותרת
            self.title_label.setText(f"פרטי מודל: {model.name}")
            
            # עדכון כפתורים
            self.activate_button.setEnabled(not model.is_active)
            self.compare_button.setEnabled(True)
            
            # עדכון מידע בסיסי
            self.name_value.setText(model.name)
            self.provider_value.setText(model.provider)
            self.version_value.setText(model.version or "לא צוין")
            
            # סטטוס
            if model.is_active:
                self.status_value.setText("🟢 פעיל")
                self.status_value.setStyleSheet("color: #4CAF50; font-weight: bold;")
            elif model.is_available:
                self.status_value.setText("🟡 זמין")
                self.status_value.setStyleSheet("color: #FFC107; font-weight: bold;")
            else:
                self.status_value.setText("🔴 לא זמין")
                self.status_value.setStyleSheet("color: #F44336; font-weight: bold;")
            
            # תיאור
            self.description_text.setPlainText(model.description)
            
            # מפרטים טכניים
            self.max_tokens_value.setText(f"{model.max_tokens:,}")
            self.context_window_value.setText(f"{model.context_window:,}")
            self.cost_per_token_value.setText(f"${model.cost_per_token:.6f}")
            self.cost_per_1k_value.setText(f"${model.cost_per_1k_tokens:.4f}")
            
            # יכולות
            self.capabilities_text.setPlainText(model.capabilities_display)
            
            # הגדרות
            self.availability_value.setText("✅ זמין" if model.is_available else "❌ לא זמין")
            self.last_update_value.setText("לא ידוע")  # יעודכן בעתיד
            self.training_cutoff_value.setText(model.training_data_cutoff or "לא צוין")
            
            # מטא-נתונים
            if model.metadata:
                metadata_text = "\n".join([f"{k}: {v}" for k, v in model.metadata.items()])
                self.metadata_text.setPlainText(metadata_text)
            else:
                self.metadata_text.setPlainText("אין מטא-נתונים זמינים")
            
            # עדכון טאב ביצועים
            self.update_performance_tab()
            
        except Exception as e:
            QMessageBox.warning(self, "שגיאה", f"לא ניתן לטעון פרטי מודל:\n{str(e)}")
            self.show_empty_state()
    
    def update_performance_tab(self):
        """עדכון טאב ביצועים"""
        if not self.current_model:
            return
        
        # ניקוי טאב קיים
        if self.performance_tab.layout():
            QWidget().setLayout(self.performance_tab.layout())
        
        # יצירת רכיב ביצועים חדש
        performance_widget = ModelPerformanceWidget(self.current_model)
        layout = QVBoxLayout(self.performance_tab)
        layout.addWidget(performance_widget)
    
    def activate_model(self):
        """הפעלת מודל"""
        if not self.current_model:
            return
        
        try:
            success = self.llm_service.set_active_model(self.current_model.id)
            if success:
                self.model_activated.emit(self.current_model.id)
                self.activate_button.setEnabled(False)
                self.status_value.setText("🟢 פעיל")
                self.status_value.setStyleSheet("color: #4CAF50; font-weight: bold;")
                QMessageBox.information(self, "הצלחה", f"מודל {self.current_model.name} הופעל בהצלחה")
            else:
                QMessageBox.warning(self, "שגיאה", "לא ניתן להפעיל את המודל")
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בהפעלת מודל:\n{str(e)}")
    
    def show_comparison(self):
        """הצגת השוואת מודלים"""
        if not self.current_model:
            return
        
        try:
            # קבלת מודלים נוספים מאותו ספק
            provider_models = self.llm_service.get_models_by_provider(self.current_model.provider)
            
            # סינון המודל הנוכחי
            other_models = [m for m in provider_models if m.id != self.current_model.id]
            
            if not other_models:
                QMessageBox.information(self, "מידע", "אין מודלים נוספים להשוואה")
                return
            
            # בחירת עד 3 מודלים להשוואה
            comparison_models = [self.current_model] + other_models[:2]
            
            # הצגת דיאלוג השוואה
            dialog = ModelComparisonDialog(comparison_models, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "שגיאה", f"לא ניתן להציג השוואה:\n{str(e)}")
    
    def add_to_comparison(self, model_id: str):
        """הוספת מודל להשוואה"""
        if model_id not in self.comparison_models:
            self.comparison_models.append(model_id)
            
            # הגבלת מספר מודלים להשוואה
            if len(self.comparison_models) > 3:
                self.comparison_models = self.comparison_models[-3:]
    
    def clear_comparison(self):
        """ניקוי רשימת השוואה"""
        self.comparison_models.clear()