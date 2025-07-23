from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal
from PyQt6.QtGui import QIcon


class ChatMessage(QFrame):
    """רכיב להצגת הודעת צ'אט בודדת"""
    
    # אותות
    file_clicked = pyqtSignal(dict)  # אות שנשלח כאשר לוחצים על קובץ מצורף
    
    def __init__(self, text, message_type="user", parent=None, timestamp=None, attachments=None):
        """
        יוצר הודעת צ'אט חדשה
        
        Args:
            text (str): תוכן ההודעה
            message_type (str): סוג ההודעה - "user", "ai", או "system"
            parent (QWidget, optional): הווידג'ט ההורה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
            attachments (list, optional): רשימת קבצים מצורפים
        """
        super().__init__(parent)
        self.message_type = message_type
        self.text = text
        self.timestamp = timestamp or QDateTime.currentDateTime()
        self.attachments = attachments or []
        
        # עיצוב הודעה
        self.setObjectName(f"{message_type}Message")
        # self.setFrameShape(QFrame.StyledPanel)  # מבוטל בגלל בעיית תאימות
        # self.setFrameShadow(QFrame.Raised)  # מבוטל בגלל בעיית תאימות
        
        # לייאאוט
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # תוכן ההודעה
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        try:
            self.text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        except AttributeError:
            try:
                self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            except AttributeError:
                # אם שום דבר לא עובד, נשתמש בערכים מספריים
                self.text_label.setTextInteractionFlags(2)  # TextSelectableByMouse = 2
        layout.addWidget(self.text_label)
        
        # קבצים מצורפים
        if self.attachments:
            for attachment in self.attachments:
                attachment_widget = self._create_attachment_widget(attachment)
                if attachment_widget:
                    layout.addWidget(attachment_widget)
        
        # זמן שליחה
        time_layout = QHBoxLayout()
        time_layout.addStretch()
        
        self.time_label = QLabel(self.timestamp.toString("HH:mm"))
        self.time_label.setStyleSheet("color: #888; font-size: 10px;")
        time_layout.addWidget(self.time_label)
        
        layout.addLayout(time_layout)
    
    def _create_attachment_widget(self, attachment):
        """יצירת ווידג'ט לקובץ מצורף"""
        if attachment.get("type") == "audio_file":
            # יצירת מסגרת לקובץ אודיו
            attachment_frame = QFrame()
            attachment_frame.setStyleSheet("""
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
                margin-top: 5px;
            """)
            
            # לייאאוט לקובץ
            attachment_layout = QHBoxLayout(attachment_frame)
            attachment_layout.setContentsMargins(5, 5, 5, 5)
            attachment_layout.setSpacing(10)
            
            # אייקון קובץ אודיו
            file_icon = QLabel("🎵")  # אימוג'י של תו מוזיקלי
            file_icon.setStyleSheet("font-size: 16px;")
            attachment_layout.addWidget(file_icon)
            
            # מידע על הקובץ
            file_info_layout = QVBoxLayout()
            
            # שם הקובץ
            file_name = QLabel(attachment.get("name", "קובץ אודיו"))
            file_name.setStyleSheet("font-weight: bold; color: #ddd;")
            file_info_layout.addWidget(file_name)
            
            # פרטי הקובץ
            file_details = []
            
            # פורמט
            if "format" in attachment:
                file_details.append(attachment["format"].upper())
            
            # גודל
            if "size" in attachment:
                size = attachment["size"]
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                file_details.append(size_str)
            
            # משך
            if "duration" in attachment and attachment["duration"] > 0:
                duration = attachment["duration"]
                minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                
                if hours > 0:
                    duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    duration_str = f"{minutes}:{seconds:02d}"
                file_details.append(duration_str)
            
            # הצגת פרטי הקובץ
            if file_details:
                details_label = QLabel(" | ".join(file_details))
                details_label.setStyleSheet("color: #888; font-size: 10px;")
                file_info_layout.addWidget(details_label)
            
            attachment_layout.addLayout(file_info_layout)
            attachment_layout.addStretch()
            
            # כפתור נגינה
            play_button = QPushButton("נגן")
            play_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            play_button.clicked.connect(lambda: self.file_clicked.emit(attachment))
            attachment_layout.addWidget(play_button)
            
            return attachment_frame
        
        return None
        
        # עיצוב לפי סוג הודעה
        self._apply_style()
    
    def _apply_style(self):
        """החלת עיצוב לפי סוג הודעה"""
        base_style = """
            border-radius: 8px;
            padding: 5px;
            margin: 2px 0;
        """
        
        if self.message_type == "user":
            self.setStyleSheet(base_style + """
                background-color: #1e1e1e;
                border: 1px solid #333;
                margin-left: 50px;
            """)
            self.text_label.setStyleSheet("color: #2196F3;")
        elif self.message_type == "ai":
            self.setStyleSheet(base_style + """
                background-color: #252525;
                border: 1px solid #333;
                margin-right: 50px;
            """)
            self.text_label.setStyleSheet("color: #4CAF50;")
        else:  # system
            self.setStyleSheet(base_style + """
                background-color: #303030;
                border: 1px solid #444;
                font-style: italic;
            """)
            self.text_label.setStyleSheet("color: #FFC107;")