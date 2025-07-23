from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSplitter, QFrame, QScrollArea, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont


class HomePage(QWidget):
    """דף הבית המשלב צ'אט והעלאת קבצים"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        
        # סגנון כללי לדף - רקע שחור וטקסט לבן
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
            }
            QFrame#chatPanel, QFrame#filePanel {
                background-color: #121212;
                border: none;
            }
            QLabel#panelTitle {
                color: white;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QTextEdit, QPushButton {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #333;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        
        # יצירת הלייאאוט הראשי
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # יצירת הפאנלים
        self.chat_panel = self._create_chat_panel()
        self.file_panel = self._create_file_panel()
        
        # הוספת הפאנלים ללייאאוט עם ספליטר
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.chat_panel)
        self.splitter.addWidget(self.file_panel)
        
        # הגדרת גדלים התחלתיים (60% לצ'אט, 40% לקבצים)
        self.splitter.setSizes([600, 400])
        
        self.main_layout.addWidget(self.splitter)
    
    def _create_chat_panel(self):
        """יצירת פאנל צ'אט"""
        panel = QFrame()
        panel.setObjectName("chatPanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # כותרת
        title = QLabel("צ'אט")
        title.setObjectName("panelTitle")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # תיאור
        description = QLabel("שוחח עם ה-AI או העלה קבצי אודיו לניתוח")
        description.setStyleSheet("color: #aaa; margin-bottom: 15px;")
        layout.addWidget(description)
        
        # אזור הודעות (פלייסהולדר)
        chat_area = QScrollArea()
        chat_area.setWidgetResizable(True)
        chat_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        chat_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        chat_content = QWidget()
        chat_layout = QVBoxLayout(chat_content)
        chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        chat_layout.addWidget(QLabel("כאן יופיעו הודעות הצ'אט"))
        chat_layout.addStretch()
        
        chat_area.setWidget(chat_content)
        layout.addWidget(chat_area, 1)  # stretch factor 1
        
        # אזור קלט
        input_layout = QHBoxLayout()
        
        chat_input = QTextEdit()
        chat_input.setPlaceholderText("הקלד הודעה...")
        chat_input.setMaximumHeight(80)
        input_layout.addWidget(chat_input)
        
        send_button = QPushButton("שלח")
        send_button.setMinimumWidth(80)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        
        return panel
    
    def _create_file_panel(self):
        """יצירת פאנל העלאת קבצים"""
        panel = QFrame()
        panel.setObjectName("filePanel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # כותרת
        title = QLabel("העלאת קבצים")
        title.setObjectName("panelTitle")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # תיאור
        description = QLabel("העלה קבצי אודיו לניתוח וצפה בקבצים האחרונים שלך")
        description.setStyleSheet("color: #aaa; margin-bottom: 15px;")
        layout.addWidget(description)
        
        # אזור העלאה (פלייסהולדר)
        upload_area = QLabel("גרור קבצי אודיו לכאן או לחץ לבחירה")
        upload_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_area.setStyleSheet("""
            border: 2px dashed #555;
            border-radius: 8px;
            padding: 30px;
            background-color: #1e1e1e;
            color: white;
        """)
        upload_area.setMinimumHeight(120)
        layout.addWidget(upload_area)
        
        # רשימת קבצים אחרונים (פלייסהולדר)
        recent_files_title = QLabel("קבצים אחרונים")
        recent_files_title.setStyleSheet("font-weight: bold; margin-top: 20px; color: white;")
        layout.addWidget(recent_files_title)
        
        recent_files_area = QScrollArea()
        recent_files_area.setWidgetResizable(True)
        recent_files_content = QWidget()
        recent_files_layout = QVBoxLayout(recent_files_content)
        recent_files_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        recent_files_layout.addWidget(QLabel("אין קבצים אחרונים להצגה"))
        
        recent_files_area.setWidget(recent_files_content)
        layout.addWidget(recent_files_area, 1)  # stretch factor 1
        
        return panel