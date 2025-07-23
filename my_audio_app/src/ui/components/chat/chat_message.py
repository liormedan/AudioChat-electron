from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QDateTime


class ChatMessage(QFrame):
    """רכיב להצגת הודעת צ'אט בודדת"""
    
    def __init__(self, text, message_type="user", parent=None, timestamp=None):
        """
        יוצר הודעת צ'אט חדשה
        
        Args:
            text (str): תוכן ההודעה
            message_type (str): סוג ההודעה - "user", "ai", או "system"
            parent (QWidget, optional): הווידג'ט ההורה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
        """
        super().__init__(parent)
        self.message_type = message_type
        self.text = text
        self.timestamp = timestamp or QDateTime.currentDateTime()
        
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
        
        # זמן שליחה
        time_layout = QHBoxLayout()
        time_layout.addStretch()
        
        self.time_label = QLabel(self.timestamp.toString("HH:mm"))
        self.time_label.setStyleSheet("color: #888; font-size: 10px;")
        time_layout.addWidget(self.time_label)
        
        layout.addLayout(time_layout)
        
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