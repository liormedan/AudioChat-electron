from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QListWidget, QListWidgetItem, QPushButton, QComboBox,
                           QGroupBox, QFormLayout, QSpinBox, QCheckBox, QSplitter,
                           QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap
import os
from datetime import datetime

from ui.components.exports import ExportDetails, ExportDialog
from models.audio_export import AudioExport
from services.export_service import ExportService


class AudioExportPage(QWidget):
    """דף ייצוא קבצי אודיו"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("audioExportPage")
        
        # סגנון כללי לדף - רקע שחור וטקסט לבן
        self.setStyleSheet("""
            QWidget {
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
            QListWidget {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
            }
            QComboBox, QPushButton, QSpinBox {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QComboBox:hover, QSpinBox:hover {
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
        
        # יצירת שירותים
        self.export_service = ExportService()
        
        # יצירת הלייאאוט הראשי
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # כותרת הדף
        title = QLabel("📤 Audio Exports")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(title)
        
        # תיאור
        description = QLabel("Export your audio files to various formats with custom settings")
        description.setStyleSheet("color: #aaa; margin-bottom: 15px;")
        main_layout.addWidget(description)
        
        # יצירת ספליטר לחלוקת המסך
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # חלק שמאלי - רשימת קבצים לייצוא
        self.splitter.addWidget(self._create_files_list())
        
        # חלק ימני - פרטי ייצוא
        self.export_details = ExportDetails()
        self.export_details.export_updated.connect(self._on_export_updated)
        self.export_details.export_deleted.connect(self._on_export_deleted)
        self.export_details.export_downloaded.connect(self._on_export_downloaded)
        self.splitter.addWidget(self.export_details)
        
        # הגדרת יחס גדלים התחלתי (60% לרשימה, 40% לפרטים)
        self.splitter.setSizes([600, 400])
        
        main_layout.addWidget(self.splitter)
        
        # כפתורי פעולה
        actions_layout = QHBoxLayout()
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # כפתור יצירת ייצוא חדש
        new_export_button = QPushButton("New Export")
        new_export_button.setFixedWidth(120)
        new_export_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        new_export_button.clicked.connect(self._on_new_export_clicked)
        actions_layout.addWidget(new_export_button)
        
        main_layout.addLayout(actions_layout)
        
        # טעינת ייצואים לדוגמה
        self._load_sample_exports()
    
    def _create_files_list(self):
        """יצירת רשימת ייצואים"""
        group_box = QGroupBox("Exports")
        
        layout = QVBoxLayout(group_box)
        
        # סרגל חיפוש
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QComboBox()
        self.search_input.setEditable(True)
        self.search_input.setPlaceholderText("Search exports...")
        self.search_input.setMinimumWidth(200)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        
        layout.addLayout(search_layout)
        
        # רשימת ייצואים
        self.exports_list = QListWidget()
        self.exports_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.exports_list.itemClicked.connect(self._on_export_selected)
        
        layout.addWidget(self.exports_list, 1)  # stretch factor 1
        
        # כפתורי פעולה
        buttons_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._load_sample_exports)
        
        filter_button = QPushButton("Filter")
        filter_button.setCheckable(True)
        
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(filter_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return group_box
        
    def _on_export_updated(self, export_id):
        """
        טיפול בעדכון ייצוא
        
        Args:
            export_id (str): מזהה הייצוא שעודכן
        """
        # בפרויקט אמיתי, כאן היינו מעדכנים את הייצוא במסד הנתונים
        print(f"Export updated: {export_id}")
    
    def _on_export_deleted(self, export_id):
        """
        טיפול במחיקת ייצוא
        
        Args:
            export_id (str): מזהה הייצוא שנמחק
        """
        # מחיקת הייצוא מהשירות
        success = self.export_service.delete_export(export_id)
        
        if success:
            # הצגת הודעת הצלחה
            QMessageBox.information(
                self,
                "Export Deleted",
                "The export has been successfully deleted."
            )
            
            # רענון רשימת הייצואים
            self._load_sample_exports()
            
            # בדיקה אם יש ייצואים נוספים
            exports = self.export_service.get_all_exports()
            if exports:
                # בחירת הייצוא הראשון
                self.export_details.set_export(exports[0])
            else:
                # אין ייצואים, ניקוי פרטי הייצוא
                self.export_details.set_export(None)
        else:
            # הצגת הודעת שגיאה
            QMessageBox.critical(
                self,
                "Delete Failed",
                "Failed to delete the export. It may be in processing state or no longer exists."
            )
    
    def _on_export_downloaded(self, export_id):
        """
        טיפול בהורדת ייצוא
        
        Args:
            export_id (str): מזהה הייצוא שהורד
        """
        # בפרויקט אמיתי, כאן היינו מעדכנים סטטיסטיקות הורדה וכו'
        print(f"Export downloaded: {export_id}")
    
    def _on_new_export_clicked(self):
        """טיפול בלחיצה על כפתור יצירת ייצוא חדש"""
        # יצירת דיאלוג ייצוא חדש
        dialog = ExportDialog(self)
        dialog.export_created.connect(self._on_export_created)
        
        # הצגת הדיאלוג
        dialog.exec()
    
    def _on_export_created(self, export_id):
        """
        טיפול ביצירת ייצוא חדש
        
        Args:
            export_id (str): מזהה הייצוא שנוצר
        """
        # רענון רשימת הייצואים
        self._load_sample_exports()
        
        # בחירת הייצוא החדש
        export = self.export_service.get_export_by_id(export_id)
        if export:
            # מציאת הפריט ברשימה
            for i in range(self.exports_list.count()):
                item = self.exports_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == export_id:
                    self.exports_list.setCurrentItem(item)
                    self.export_details.set_export(export)
                    break
            
            # הצגת הודעת הצלחה
            QMessageBox.information(
                self,
                "Export Created",
                f"The export '{export.name}' has been created and is now processing.\n\n"
                "You can monitor its progress in the exports list."
            )
    
    def _on_export_selected(self, item):
        """
        טיפול בבחירת ייצוא מהרשימה
        
        Args:
            item (QListWidgetItem): הפריט שנבחר
        """
        # קבלת מזהה הייצוא מהפריט
        export_id = item.data(Qt.ItemDataRole.UserRole)
        
        # קבלת הייצוא מהשירות
        export = self.export_service.get_export_by_id(export_id)
        
        # הצגת פרטי הייצוא
        if export:
            self.export_details.set_export(export)
    
    def _load_sample_exports(self):
        """טעינת ייצואים לדוגמה"""
        # קבלת כל הייצואים מהשירות
        exports = self.export_service.get_all_exports()
        
        # אם אין ייצואים, יצירת ייצואים לדוגמה
        if not exports:
            self._create_sample_exports()
            exports = self.export_service.get_all_exports()
        
        # עדכון רשימת הייצואים
        self.exports_list.clear()
        
        for export in exports:
            item = QListWidgetItem()
            item.setText(f"{export.name} ({export.format.upper()})")
            item.setData(Qt.ItemDataRole.UserRole, export.id)
            
            # הוספת סטטוס לטקסט
            status_symbol = "✓" if export.status == "completed" else "⏳" if export.status == "processing" else "❌"
            item.setText(f"{status_symbol} {export.name} ({export.format.upper()})")
            
            # הוספת מידע נוסף כטולטיפ
            item.setToolTip(
                f"Name: {export.name}\n"
                f"Format: {export.format.upper()}\n"
                f"Size: {export.size_formatted}\n"
                f"Duration: {export.duration_formatted}\n"
                f"Created: {export.created_at_formatted}\n"
                f"Status: {export.status.capitalize()}"
            )
            
            self.exports_list.addItem(item)
        
        # בחירת ייצוא ראשון להצגה
        if exports and self.exports_list.count() > 0:
            self.exports_list.setCurrentRow(0)
            self.export_details.set_export(exports[0])
    
    def _create_sample_exports(self):
        """יצירת ייצואים לדוגמה"""
        # יצירת ייצוא MP3
        self.export_service.create_export(
            source_file_id="sample1",
            format="mp3",
            name="Interview_001.mp3",
            settings={
                "bitrate": "320 kbps",
                "sample_rate": "48 kHz",
                "channels": "Stereo (2)",
                "normalize": True,
                "noise_reduction": False
            }
        )
        
        # יצירת ייצוא WAV
        self.export_service.create_export(
            source_file_id="sample2",
            format="wav",
            name="Voice_Note_123.wav",
            settings={
                "bitrate": "N/A",
                "sample_rate": "44.1 kHz",
                "channels": "Mono (1)",
                "normalize": False,
                "noise_reduction": True
            }
        )
        
        # יצירת ייצוא FLAC
        self.export_service.create_export(
            source_file_id="sample3",
            format="flac",
            name="Meeting_Recording.flac",
            settings={
                "bitrate": "N/A",
                "sample_rate": "96 kHz",
                "channels": "Stereo (2)",
                "normalize": True,
                "noise_reduction": True
            }
        )