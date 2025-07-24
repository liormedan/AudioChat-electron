from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QListWidget, QListWidgetItem, QPushButton, QComboBox,
                           QGroupBox, QFormLayout, QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal


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
        
        # יצירת לייאאוט לשני חלקים
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # חלק שמאלי - רשימת קבצים לייצוא
        content_layout.addWidget(self._create_files_list(), 1)
        
        # חלק ימני - הגדרות ייצוא
        content_layout.addWidget(self._create_export_settings(), 1)
        
        main_layout.addLayout(content_layout)
        
        # כפתורי פעולה
        actions_layout = QHBoxLayout()
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # כפתור ביטול
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(120)
        actions_layout.addWidget(cancel_button)
        
        # כפתור ייצוא
        export_button = QPushButton("Export Files")
        export_button.setFixedWidth(120)
        export_button.setStyleSheet("""
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
        actions_layout.addWidget(export_button)
        
        main_layout.addLayout(actions_layout)
        
        # מרווח בסוף
        main_layout.addStretch()
    
    def _create_files_list(self):
        """יצירת רשימת קבצים לייצוא"""
        group_box = QGroupBox("Files to Export")
        
        layout = QVBoxLayout(group_box)
        
        # רשימת קבצים
        self.files_list = QListWidget()
        
        # הוספת קבצי דוגמה
        sample_files = [
            "Interview_001.mp3",
            "Voice_Note_123.wav",
            "Meeting_Recording.flac",
            "Audio_Book_Ch1.mp3",
            "Podcast_Episode5.mp3",
        ]
        
        for file in sample_files:
            item = QListWidgetItem(file)
            item.setCheckState(Qt.CheckState.Checked)
            self.files_list.addItem(item)
        
        layout.addWidget(self.files_list)
        
        # כפתורי פעולה
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Files")
        select_all_button = QPushButton("Select All")
        clear_button = QPushButton("Clear")
        
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(select_all_button)
        buttons_layout.addWidget(clear_button)
        
        layout.addLayout(buttons_layout)
        
        return group_box
    
    def _create_export_settings(self):
        """יצירת הגדרות ייצוא"""
        group_box = QGroupBox("Export Settings")
        
        layout = QVBoxLayout(group_box)
        
        # טופס הגדרות
        form_layout = QFormLayout()
        
        # פורמט ייצוא
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP3", "WAV", "FLAC", "OGG", "M4A"])
        form_layout.addRow("Export Format:", self.format_combo)
        
        # איכות
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Very High"])
        self.quality_combo.setCurrentIndex(2)  # High by default
        form_layout.addRow("Quality:", self.quality_combo)
        
        # קצב סיביות
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["128 kbps", "192 kbps", "256 kbps", "320 kbps"])
        self.bitrate_combo.setCurrentIndex(2)  # 256 kbps by default
        form_layout.addRow("Bitrate:", self.bitrate_combo)
        
        # קצב דגימה
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["44.1 kHz", "48 kHz", "96 kHz"])
        self.sample_rate_combo.setCurrentIndex(1)  # 48 kHz by default
        form_layout.addRow("Sample Rate:", self.sample_rate_combo)
        
        # ערוצים
        self.channels_combo = QComboBox()
        self.channels_combo.addItems(["Mono (1)", "Stereo (2)"])
        self.channels_combo.setCurrentIndex(1)  # Stereo by default
        form_layout.addRow("Channels:", self.channels_combo)
        
        layout.addLayout(form_layout)
        
        # הגדרות נוספות
        additional_settings = QGroupBox("Additional Settings")
        additional_layout = QVBoxLayout(additional_settings)
        
        # נרמול עוצמה
        self.normalize_check = QCheckBox("Normalize Volume")
        self.normalize_check.setChecked(True)
        additional_layout.addWidget(self.normalize_check)
        
        # הסרת רעשים
        self.noise_reduction_check = QCheckBox("Apply Noise Reduction")
        additional_layout.addWidget(self.noise_reduction_check)
        
        # הוספת מטא-דאטה
        self.metadata_check = QCheckBox("Include Metadata")
        self.metadata_check.setChecked(True)
        additional_layout.addWidget(self.metadata_check)
        
        # יצירת תיקיות לפי תאריך
        self.folders_check = QCheckBox("Create Date-based Folders")
        additional_layout.addWidget(self.folders_check)
        
        layout.addWidget(additional_settings)
        
        # תיקיית יעד
        destination_layout = QHBoxLayout()
        destination_layout.addWidget(QLabel("Destination:"))
        
        destination_path = QLabel("C:/Users/User/Music/Exports")
        destination_path.setStyleSheet("color: #aaa;")
        destination_layout.addWidget(destination_path, 1)
        
        browse_button = QPushButton("Browse...")
        browse_button.setFixedWidth(100)
        destination_layout.addWidget(browse_button)
        
        layout.addLayout(destination_layout)
        
        return group_box