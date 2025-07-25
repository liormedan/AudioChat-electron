from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QSpinBox, QCheckBox, QPushButton, QFileDialog,
                           QFormLayout, QGroupBox, QMessageBox, QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon

import os
from typing import Dict, Any, Optional, List

from services.file_service import FileService
from services.export_service import ExportService
from ui.components.file_upload.file_info import FileInfo


class ExportDialog(QDialog):
    """דיאלוג ליצירת ייצוא חדש"""
    
    # אות שנשלח כאשר נוצר ייצוא חדש
    export_created = pyqtSignal(str)  # מזהה הייצוא החדש
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Audio Export")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setModal(True)
        
        # שירותים
        self.file_service = FileService()
        self.export_service = ExportService()
        
        # מקור הקובץ הנבחר
        self.selected_file: Optional[FileInfo] = None
        
        # יצירת ממשק
        self._init_ui()
        
        # טעינת פורמטים זמינים
        self._load_formats()
        
        # טעינת קבצי מקור
        self._load_source_files()
    
    def _init_ui(self):
        """יצירת ממשק המשתמש"""
        # סגנון כללי
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: white;
            }
            QGroupBox {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
            QLabel {
                color: white;
            }
            QComboBox, QPushButton, QSpinBox, QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover, QComboBox:hover, QSpinBox:hover {
                border: 1px solid #555;
            }
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        
        # לייאאוט ראשי
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # כותרת
        title = QLabel("Create New Export")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # קבוצת בחירת קובץ מקור
        source_group = QGroupBox("Source File")
        source_layout = QFormLayout(source_group)
        
        # בחירת קובץ מקור
        self.source_combo = QComboBox()
        self.source_combo.setMinimumWidth(300)
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        
        # כפתור לבחירת קובץ חיצוני
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._on_browse_clicked)
        
        # לייאאוט לבחירת קובץ
        source_file_layout = QHBoxLayout()
        source_file_layout.addWidget(self.source_combo)
        source_file_layout.addWidget(browse_button)
        
        source_layout.addRow("Select File:", source_file_layout)
        
        # מידע על הקובץ הנבחר
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setStyleSheet("color: #aaa; font-style: italic;")
        source_layout.addRow("File Info:", self.file_info_label)
        
        main_layout.addWidget(source_group)
        
        # קבוצת הגדרות ייצוא
        export_group = QGroupBox("Export Settings")
        export_layout = QFormLayout(export_group)
        
        # שם הייצוא
        self.name_edit = QLineEdit()
        export_layout.addRow("Export Name:", self.name_edit)
        
        # פורמט
        self.format_combo = QComboBox()
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        export_layout.addRow("Format:", self.format_combo)
        
        # איכות (ביטרייט)
        self.quality_combo = QComboBox()
        export_layout.addRow("Quality:", self.quality_combo)
        
        # קצב דגימה
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["44.1 kHz", "48 kHz", "96 kHz", "192 kHz"])
        self.sample_rate_combo.setCurrentIndex(1)  # 48 kHz כברירת מחדל
        export_layout.addRow("Sample Rate:", self.sample_rate_combo)
        
        # ערוצים
        self.channels_combo = QComboBox()
        self.channels_combo.addItems(["Mono (1)", "Stereo (2)"])
        self.channels_combo.setCurrentIndex(1)  # סטריאו כברירת מחדל
        export_layout.addRow("Channels:", self.channels_combo)
        
        main_layout.addWidget(export_group)
        
        # קבוצת עיבוד
        processing_group = QGroupBox("Processing Options")
        processing_layout = QFormLayout(processing_group)
        
        # נרמול עוצמה
        self.normalize_check = QCheckBox("Apply volume normalization")
        processing_layout.addRow("", self.normalize_check)
        
        # הסרת רעשים
        self.noise_removal_check = QCheckBox("Apply noise reduction")
        processing_layout.addRow("", self.noise_removal_check)
        
        main_layout.addWidget(processing_group)
        
        # כפתורי פעולה
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        
        # עיצוב כפתורים
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Create Export")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Cancel")
        
        main_layout.addWidget(button_box)
    
    def _load_formats(self):
        """טעינת פורמטים זמינים"""
        formats = self.export_service.get_export_formats()
        self.format_combo.addItems([fmt.upper() for fmt in formats])
        self._on_format_changed(0)  # עדכון אפשרויות איכות לפורמט הראשון
    
    def _load_source_files(self):
        """טעינת קבצי מקור זמינים"""
        # קבלת קבצים אחרונים
        recent_files = self.file_service.get_recent_files(limit=10)
        
        # הוספת הקבצים לקומבו
        self.source_combo.clear()
        self.source_combo.addItem("Select a file...", None)
        
        for file_info in recent_files:
            self.source_combo.addItem(file_info.name, file_info)
    
    def _on_source_changed(self, index):
        """
        טיפול בשינוי בחירת קובץ מקור
        
        Args:
            index (int): האינדקס שנבחר
        """
        if index <= 0:
            self.selected_file = None
            self.file_info_label.setText("No file selected")
            self.name_edit.setText("")
            return
        
        # קבלת אובייקט FileInfo מהקומבו
        self.selected_file = self.source_combo.currentData()
        
        if self.selected_file:
            # הצגת מידע על הקובץ
            self.file_info_label.setText(
                f"Format: {self.selected_file.format.upper()}, "
                f"Size: {self.selected_file.size_formatted}, "
                f"Duration: {self.selected_file.duration_formatted}"
            )
            
            # הגדרת שם ברירת מחדל לייצוא
            default_name = f"{os.path.splitext(self.selected_file.name)[0]}"
            self.name_edit.setText(default_name)
    
    def _on_browse_clicked(self):
        """טיפול בלחיצה על כפתור עיון"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            os.path.expanduser("~"),
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a *.aac);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # יצירת אובייקט FileInfo מהקובץ שנבחר
        file_info = FileInfo.from_file_path(file_path)
        
        # הוספת הקובץ לקומבו
        self.source_combo.addItem(file_info.name, file_info)
        self.source_combo.setCurrentIndex(self.source_combo.count() - 1)
        
        # שמירת מידע על הקובץ במסד הנתונים
        self.file_service.save_file_info(file_info)
    
    def _on_format_changed(self, index):
        """
        טיפול בשינוי פורמט
        
        Args:
            index (int): האינדקס שנבחר
        """
        # קבלת הפורמט הנבחר
        format_text = self.format_combo.currentText().lower()
        
        # עדכון אפשרויות איכות בהתאם לפורמט
        self.quality_combo.clear()
        
        if format_text == "mp3":
            self.quality_combo.addItems(["128 kbps", "192 kbps", "256 kbps", "320 kbps"])
            self.quality_combo.setCurrentIndex(2)  # 256 kbps כברירת מחדל
        elif format_text == "ogg":
            self.quality_combo.addItems(["Low (96 kbps)", "Medium (128 kbps)", "High (192 kbps)", "Very High (256 kbps)"])
            self.quality_combo.setCurrentIndex(2)  # High כברירת מחדל
        elif format_text == "m4a" or format_text == "aac":
            self.quality_combo.addItems(["Low (96 kbps)", "Medium (128 kbps)", "High (192 kbps)", "Very High (256 kbps)"])
            self.quality_combo.setCurrentIndex(2)  # High כברירת מחדל
        elif format_text == "flac":
            self.quality_combo.addItems(["Level 0 (Fastest)", "Level 5 (Default)", "Level 8 (Best Compression)"])
            self.quality_combo.setCurrentIndex(1)  # Level 5 כברירת מחדל
        elif format_text == "wav":
            self.quality_combo.addItems(["16-bit PCM", "24-bit PCM", "32-bit Float"])
            self.quality_combo.setCurrentIndex(0)  # 16-bit PCM כברירת מחדל
        else:
            self.quality_combo.addItems(["Default"])
    
    def _validate_input(self) -> bool:
        """
        בדיקת תקינות הקלט
        
        Returns:
            bool: האם הקלט תקין
        """
        # בדיקה שנבחר קובץ מקור
        if not self.selected_file:
            QMessageBox.warning(
                self,
                "Missing Source File",
                "Please select a source audio file."
            )
            return False
        
        # בדיקה ששם הייצוא לא ריק
        export_name = self.name_edit.text().strip()
        if not export_name:
            QMessageBox.warning(
                self,
                "Missing Export Name",
                "Please enter a name for the export."
            )
            self.name_edit.setFocus()
            return False
        
        # בדיקה ששם הייצוא תקין
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in export_name:
                QMessageBox.warning(
                    self,
                    "Invalid Export Name",
                    f"The export name contains invalid characters: {', '.join(invalid_chars)}"
                )
                self.name_edit.setFocus()
                return False
        
        return True
    
    def _on_accept(self):
        """טיפול בלחיצה על כפתור אישור"""
        # בדיקת תקינות הקלט
        if not self._validate_input():
            return
        
        # הכנת נתוני הייצוא
        export_name = self.name_edit.text().strip()
        format_text = self.format_combo.currentText().lower()
        
        # הכנת הגדרות
        settings = {
            "bitrate": self.quality_combo.currentText(),
            "sample_rate": self.sample_rate_combo.currentText(),
            "channels": self.channels_combo.currentText(),
            "normalize": self.normalize_check.isChecked(),
            "noise_reduction": self.noise_removal_check.isChecked()
        }
        
        try:
            # יצירת הייצוא
            export = self.export_service.create_export(
                source_file_id=self.selected_file.path,
                format=format_text,
                name=export_name,
                settings=settings
            )
            
            # שליחת אות על יצירת ייצוא חדש
            self.export_created.emit(export.id)
            
            # סגירת הדיאלוג
            self.accept()
            
        except Exception as e:
            # הצגת הודעת שגיאה
            QMessageBox.critical(
                self,
                "Export Creation Failed",
                f"Failed to create the export: {str(e)}"
            )
