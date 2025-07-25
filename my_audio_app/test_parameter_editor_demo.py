#!/usr/bin/env python3
"""
דמו לרכיב ParameterEditor
מציג את הרכיב ומאפשר בדיקה ידנית של הפונקציונליות
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt

# הוספת נתיב הפרויקט
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.components.llm.parameter_editor import ParameterEditor
from src.models.llm_models import LLMParameters


class ParameterEditorDemo(QMainWindow):
    """חלון דמו לעורך פרמטרים"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parameter Editor Demo")
        self.setGeometry(100, 100, 1000, 800)
        
        # יצירת הווידג'ט המרכזי
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # לייאאוט ראשי
        main_layout = QHBoxLayout(central_widget)
        
        # עורך הפרמטרים
        self.parameter_editor = ParameterEditor()
        self.parameter_editor.parameters_changed.connect(self.on_parameters_changed)
        self.parameter_editor.preset_loaded.connect(self.on_preset_loaded)
        
        main_layout.addWidget(self.parameter_editor, 2)
        
        # פאנל מידע
        info_panel = self._create_info_panel()
        main_layout.addWidget(info_panel, 1)
        
        # עדכון ראשוני
        self.update_info_display()
    
    def _create_info_panel(self) -> QWidget:
        """יצירת פאנל מידע"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # כותרת
        title = QLabel("Parameter Info")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # תצוגת פרמטרים נוכחיים
        current_group = QGroupBox("Current Parameters")
        current_layout = QVBoxLayout(current_group)
        
        self.current_params_text = QTextEdit()
        self.current_params_text.setMaximumHeight(200)
        self.current_params_text.setReadOnly(True)
        current_layout.addWidget(self.current_params_text)
        
        layout.addWidget(current_group)
        
        # לוג אירועים
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)
        
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        log_layout.addWidget(self.event_log)
        
        layout.addWidget(log_group)
        
        # כפתורי בדיקה
        test_group = QGroupBox("Test Actions")
        test_layout = QVBoxLayout(test_group)
        
        # כפתור בדיקת תקינות
        validate_btn = QPushButton("Validate Parameters")
        validate_btn.clicked.connect(self.test_validation)
        test_layout.addWidget(validate_btn)
        
        # כפתור ייצוא
        export_btn = QPushButton("Export Parameters")
        export_btn.clicked.connect(self.test_export)
        test_layout.addWidget(export_btn)
        
        # כפתור ייבוא דמו
        import_btn = QPushButton("Import Demo Parameters")
        import_btn.clicked.connect(self.test_import)
        test_layout.addWidget(import_btn)
        
        # כפתור איפוס
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.parameter_editor._reset_to_default)
        test_layout.addWidget(reset_btn)
        
        layout.addWidget(test_group)
        
        return panel
    
    def on_parameters_changed(self, params_dict):
        """טיפול בשינוי פרמטרים"""
        self.log_event(f"Parameters changed: {params_dict}")
        self.update_info_display()
    
    def on_preset_loaded(self, preset_name):
        """טיפול בטעינת פרסט"""
        self.log_event(f"Preset loaded: {preset_name}")
        self.update_info_display()
    
    def update_info_display(self):
        """עדכון תצוגת המידע"""
        params = self.parameter_editor.get_parameters()
        
        info_text = f"""Temperature: {params.temperature}
Max Tokens: {params.max_tokens}
Top P: {params.top_p}
Frequency Penalty: {params.frequency_penalty}
Presence Penalty: {params.presence_penalty}
Stop Sequences: {params.stop_sequences}

Validation: {"✅ Valid" if params.validate() else "❌ Invalid"}"""
        
        self.current_params_text.setPlainText(info_text)
    
    def log_event(self, message):
        """רישום אירוע בלוג"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")
    
    def test_validation(self):
        """בדיקת תקינות פרמטרים"""
        valid, message = self.parameter_editor.validate_parameters()
        self.log_event(f"Validation result: {message}")
    
    def test_export(self):
        """בדיקת ייצוא פרמטרים"""
        exported = self.parameter_editor.export_parameters()
        self.log_event(f"Exported parameters: {exported}")
    
    def test_import(self):
        """בדיקת ייבוא פרמטרים דמו"""
        demo_params = {
            "temperature": 0.85,
            "max_tokens": 1500,
            "top_p": 0.95,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.1,
            "stop_sequences": ["END", "STOP"]
        }
        
        success = self.parameter_editor.import_parameters(demo_params)
        if success:
            self.log_event("Demo parameters imported successfully")
        else:
            self.log_event("Failed to import demo parameters")


def main():
    """פונקציה ראשית"""
    app = QApplication(sys.argv)
    
    # הגדרת עיצוב כהה
    app.setStyleSheet("""
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
            border: 1px solid #555;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #505050;
            border-color: #777;
        }
        QPushButton:pressed {
            background-color: #353535;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 4px;
        }
        QLabel {
            color: #ffffff;
        }
    """)
    
    # יצירת החלון הראשי
    window = ParameterEditorDemo()
    window.show()
    
    # הרצת האפליקציה
    sys.exit(app.exec())


if __name__ == '__main__':
    main()