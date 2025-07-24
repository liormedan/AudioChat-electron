from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFormLayout, QPushButton, QGroupBox, QFrame,
                           QScrollArea, QMessageBox, QFileDialog, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap

import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from models.audio_export import AudioExport
from services.file_service import FileService
from services.export_service import ExportService


class WaveformVisualization(QFrame):
    """רכיב להצגת ויזואליזציה של צורת הגל"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border: 1px solid #333;
            border-radius: 4px;
        """)
        
        # לייאאוט
        layout = QVBoxLayout(self)
        
        # תווית
        self.placeholder = QLabel("Waveform Visualization")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.placeholder)
    
    def set_audio_data(self, audio_data=None):
        """
        הגדרת נתוני אודיו לויזואליזציה
        
        Args:
            audio_data: נתוני האודיו (לא מיושם בגרסה זו)
        """
        # בגרסה עתידית, כאן נציג את צורת הגל האמיתית
        pass


class ExportDetails(QWidget):
    """רכיב להצגת פרטי ייצוא"""
    
    # אותות
    export_updated = pyqtSignal(str)  # אות שנשלח כאשר ייצוא מתעדכן (מזהה הייצוא)
    export_deleted = pyqtSignal(str)  # אות שנשלח כאשר ייצוא נמחק (מזהה הייצוא)
    export_downloaded = pyqtSignal(str)  # אות שנשלח כאשר ייצוא מורד (מזהה הייצוא)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("exportDetails")
        
        # שירותים
        self.file_service = FileService()
        self.export_service = ExportService()
        
        # סגנון כללי
        self.setStyleSheet("""
            QWidget#exportDetails {
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
            QLabel.fieldValue {
                color: #ddd;
                font-weight: normal;
            }
            QLabel.fieldName {
                color: #aaa;
                font-weight: bold;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton#downloadButton {
                background-color: #2196F3;
                border: none;
            }
            QPushButton#downloadButton:hover {
                background-color: #1976D2;
            }
            QPushButton#deleteButton {
                background-color: #f44336;
                border: none;
            }
            QPushButton#deleteButton:hover {
                background-color: #d32f2f;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # לייאאוט ראשי
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)
        
        # אזור גלילה
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # תוכן
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        
        # כותרת
        self.title = QLabel("Export Details")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.content_layout.addWidget(self.title)
        
        # מצב ריק
        self.empty_state = QWidget()
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_text = QLabel("📤\n\nSelect an export to view details")
        empty_text.setStyleSheet("color: #888; font-size: 16px;")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_layout.addWidget(empty_text)
        empty_layout.addStretch()
        
        # פרטי ייצוא
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(20)
        
        # ויזואליזציה של צורת הגל
        self.waveform = WaveformVisualization()
        self.details_layout.addWidget(self.waveform)
        
        # מידע בסיסי
        self.basic_info = QGroupBox("Basic Information")
        basic_layout = QFormLayout(self.basic_info)
        basic_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        basic_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        basic_layout.setSpacing(10)
        
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-weight: bold;")
        self.format_label = QLabel()
        self.size_label = QLabel()
        self.duration_label = QLabel()
        self.created_label = QLabel()
        self.status_label = QLabel()
        
        basic_layout.addRow("Name:", self.name_label)
        basic_layout.addRow("Format:", self.format_label)
        basic_layout.addRow("Size:", self.size_label)
        basic_layout.addRow("Duration:", self.duration_label)
        basic_layout.addRow("Created:", self.created_label)
        basic_layout.addRow("Status:", self.status_label)
        
        self.details_layout.addWidget(self.basic_info)
        
        # הגדרות ייצוא
        self.export_settings = QGroupBox("Export Settings")
        settings_layout = QFormLayout(self.export_settings)
        settings_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        settings_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        settings_layout.setSpacing(10)
        
        self.bitrate_label = QLabel()
        self.sample_rate_label = QLabel()
        self.channels_label = QLabel()
        self.normalize_label = QLabel()
        self.noise_reduction_label = QLabel()
        
        settings_layout.addRow("Bitrate:", self.bitrate_label)
        settings_layout.addRow("Sample Rate:", self.sample_rate_label)
        settings_layout.addRow("Channels:", self.channels_label)
        settings_layout.addRow("Normalize Volume:", self.normalize_label)
        settings_layout.addRow("Noise Reduction:", self.noise_reduction_label)
        
        self.details_layout.addWidget(self.export_settings)
        
        # כפתורי פעולה
        self.actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(self.actions_group)
        
        self.download_button = QPushButton("⬇️ Download")
        self.download_button.setObjectName("downloadButton")
        self.download_button.clicked.connect(self._on_download_clicked)
        
        self.rename_button = QPushButton("✏️ Rename")
        self.rename_button.clicked.connect(self._on_rename_clicked)
        
        self.delete_button = QPushButton("🗑️ Delete")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self._on_delete_clicked)
        
        actions_layout.addWidget(self.download_button)
        actions_layout.addWidget(self.rename_button)
        actions_layout.addWidget(self.delete_button)
        
        self.details_layout.addWidget(self.actions_group)
        
        # הוספת מרווח בסוף
        self.details_layout.addStretch()
        
        # הוספת הרכיבים ללייאאוט הראשי
        self.content_layout.addWidget(self.details_widget)
        self.content_layout.addWidget(self.empty_state)
        
        # הגדרת הרכיב הנוכחי
        self.scroll_area.setWidget(self.content)
        self.layout.addWidget(self.scroll_area)
        
        # מצב התחלתי - ריק
        self._current_export = None
        self._show_empty_state()
    
    def _show_empty_state(self):
        """הצגת מצב ריק"""
        self.empty_state.setVisible(True)
        self.details_widget.setVisible(False)
        self.title.setText("Export Details")
    
    def _show_details(self):
        """הצגת פרטי ייצוא"""
        self.empty_state.setVisible(False)
        self.details_widget.setVisible(True)
    
    def set_export(self, export: Optional[AudioExport]):
        """
        הגדרת ייצוא להצגה
        
        Args:
            export (Optional[AudioExport]): אובייקט הייצוא או None לניקוי
        """
        self._current_export = export
        
        if export is None:
            self._show_empty_state()
            return
        
        # הצגת פרטים
        self._show_details()
        
        # עדכון כותרת
        self.title.setText(f"Export: {export.name}")
        
        # עדכון מידע בסיסי
        self.name_label.setText(export.name)
        self.format_label.setText(export.format.upper())
        self.size_label.setText(export.size_formatted)
        self.duration_label.setText(export.duration_formatted)
        self.created_label.setText(export.created_at_formatted)
        
        # עדכון סטטוס עם צבע מתאים
        status_text = export.status.capitalize()
        status_style = ""
        if export.status == "completed":
            status_style = "color: #4CAF50;"  # ירוק
        elif export.status == "processing":
            status_style = "color: #2196F3;"  # כחול
        elif export.status == "failed":
            status_style = "color: #F44336;"  # אדום
        
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(status_style)
        
        # עדכון הגדרות ייצוא
        settings = export.settings
        
        self.bitrate_label.setText(settings.get("bitrate", "N/A"))
        self.sample_rate_label.setText(settings.get("sample_rate", "N/A"))
        self.channels_label.setText(settings.get("channels", "N/A"))
        
        normalize = settings.get("normalize", False)
        self.normalize_label.setText("Yes" if normalize else "No")
        
        noise_reduction = settings.get("noise_reduction", False)
        self.noise_reduction_label.setText("Yes" if noise_reduction else "No")
        
        # עדכון מצב כפתורים
        self.download_button.setEnabled(export.is_completed)
        self.rename_button.setEnabled(export.is_completed)
        self.delete_button.setEnabled(not export.is_processing)
    
    def _on_download_clicked(self):
        """טיפול בלחיצה על כפתור הורדה"""
        if not self._current_export or not self._current_export.is_completed:
            return
        
        # בחירת מיקום לשמירת הקובץ
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export",
            os.path.join(os.path.expanduser("~"), self._current_export.name),
            f"{self._current_export.format.upper()} Files (*.{self._current_export.format.lower()})"
        )
        
        if not file_path:
            return
        
        # העתקת הקובץ באמצעות FileService
        if self.file_service.copy_file(self._current_export.path, file_path):
            # שליחת אות
            self.export_downloaded.emit(self._current_export.id)
            
            # הצגת הודעת הצלחה
            QMessageBox.information(
                self,
                "Download Successful",
                f"The export has been saved to:\n{file_path}"
            )
        else:
            # הצגת הודעת שגיאה
            QMessageBox.critical(
                self,
                "Download Failed",
                f"Failed to save the export to {file_path}.\nPlease check file permissions and disk space."
            )
    
    def _on_rename_clicked(self):
        """טיפול בלחיצה על כפתור שינוי שם"""
        if not self._current_export:
            return
        
        # בקשת שם חדש
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Export",
            "Enter new name:",
            text=self._current_export.name
        )
        
        if not ok or not new_name:
            return
        
        # בדיקת תקינות השם
        is_valid, error_message = self.file_service.validate_file_name(new_name)
        if not is_valid:
            QMessageBox.warning(
                self,
                "Invalid Name",
                error_message
            )
            return
        
        # שינוי שם הקובץ בדיסק
        success, new_path = self.file_service.rename_file(self._current_export.path, new_name)
        
        if success:
            # עדכון הייצוא במסד הנתונים
            old_name = self._current_export.name
            self._current_export.name = new_name
            self._current_export.path = new_path
            
            # עדכון הייצוא בשירות
            if self.export_service.update_export(self._current_export):
                # עדכון הממשק
                self.name_label.setText(new_name)
                self.title.setText(f"Export: {new_name}")
                
                # שליחת אות עדכון
                self.export_updated.emit(self._current_export.id)
                
                # הצגת הודעת הצלחה
                QMessageBox.information(
                    self,
                    "Rename Successful",
                    f"Export renamed from '{old_name}' to '{new_name}'."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Rename Partially Failed",
                    f"The file was renamed, but the database update failed.\nPlease refresh the exports list."
                )
        else:
            QMessageBox.critical(
                self,
                "Rename Failed",
                f"Failed to rename the export.\nPlease check file permissions and ensure the name is not already in use."
            )
    
    def _on_delete_clicked(self):
        """טיפול בלחיצה על כפתור מחיקה"""
        if not self._current_export:
            return
        
        # אישור מחיקה
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the export '{self._current_export.name}'?\n\nThis will permanently delete the file from disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # מחיקת הקובץ מהדיסק
        file_deleted = self.file_service.delete_file_from_disk(self._current_export.path)
        
        # מחיקת הרשומה ממסד הנתונים
        db_deleted = self.export_service.delete_export(self._current_export.id)
        
        if file_deleted and db_deleted:
            # שליחת אות מחיקה
            self.export_deleted.emit(self._current_export.id)
            
            # ניקוי הממשק
            self._current_export = None
            self._show_empty_state()
            
            # הצגת הודעת הצלחה
            QMessageBox.information(
                self,
                "Delete Successful",
                "The export has been successfully deleted."
            )
        else:
            # הצגת הודעת שגיאה
            error_message = ""
            if not file_deleted:
                error_message += "Failed to delete the file from disk.\n"
            if not db_deleted:
                error_message += "Failed to delete the record from the database.\n"
            
            QMessageBox.critical(
                self,
                "Delete Failed",
                f"{error_message}\nPlease try again or contact support."
            )