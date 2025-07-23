from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal
from .chat_message import ChatMessage


class ChatHistory(QScrollArea):
    """רכיב להצגת היסטוריית צ'אט"""
    
    # אותות
    message_clicked = pyqtSignal(int)  # אות שנשלח כאשר לוחצים על הודעה
    
    def __init__(self, parent=None):
        """
        יוצר רכיב היסטוריית צ'אט חדש
        
        Args:
            parent (QWidget, optional): הווידג'ט ההורה
        """
        super().__init__(parent)
        self.setWidgetResizable(True)
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        try:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        except AttributeError:
            try:
                self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            except AttributeError:
                # אם שום דבר לא עובד, נשתמש בערכים מספריים
                self.setHorizontalScrollBarPolicy(1)  # ScrollBarAlwaysOff = 1
                self.setVerticalScrollBarPolicy(0)  # ScrollBarAsNeeded = 0
        
        # עיצוב
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # יצירת ווידג'ט פנימי
        self.container = QWidget()
        self.container.setObjectName("chatHistoryContainer")
        self.container.setStyleSheet("background-color: transparent;")
        self.setWidget(self.container)
        
        # לייאאוט להודעות
        self.layout = QVBoxLayout(self.container)
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        try:
            self.layout.setAlignment(Qt.AlignTop)
        except AttributeError:
            try:
                self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            except AttributeError:
                # אם שום דבר לא עובד, נשתמש בערכים מספריים
                self.layout.setAlignment(0x0001)  # AlignTop = 0x0001
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # מצב ריק
        self.empty_label = QLabel("אין הודעות להצגה. התחל שיחה חדשה!")
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        try:
            self.empty_label.setAlignment(Qt.AlignCenter)
        except AttributeError:
            try:
                self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except AttributeError:
                # אם שום דבר לא עובד, נשתמש בערכים מספריים
                self.empty_label.setAlignment(0x0004 | 0x0080)  # AlignCenter = AlignHCenter | AlignVCenter
        self.empty_label.setStyleSheet("color: #888; margin: 20px;")
        self.layout.addWidget(self.empty_label)
        
        # הוספת מרווח בסוף
        self.layout.addStretch()
        
        # מעקב אחר הודעות
        self.messages = []
        self.is_empty = True
    
    def add_user_message(self, text, timestamp=None):
        """
        הוספת הודעת משתמש
        
        Args:
            text (str): תוכן ההודעה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
        
        Returns:
            ChatMessage: הודעת הצ'אט שנוצרה
        """
        message = ChatMessage(text, "user", timestamp=timestamp)
        return self._add_message(message)
    
    def add_ai_message(self, text, timestamp=None):
        """
        הוספת הודעת AI
        
        Args:
            text (str): תוכן ההודעה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
        
        Returns:
            ChatMessage: הודעת הצ'אט שנוצרה
        """
        message = ChatMessage(text, "ai", timestamp=timestamp)
        return self._add_message(message)
    
    def add_system_message(self, text, timestamp=None):
        """
        הוספת הודעת מערכת
        
        Args:
            text (str): תוכן ההודעה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
        
        Returns:
            ChatMessage: הודעת הצ'אט שנוצרה
        """
        message = ChatMessage(text, "system", timestamp=timestamp)
        return self._add_message(message)
    
    def _add_message(self, message):
        """
        הוספת הודעה ללייאאוט
        
        Args:
            message (ChatMessage): הודעת הצ'אט להוספה
        
        Returns:
            ChatMessage: הודעת הצ'אט שנוספה
        """
        # הסרת תווית ריקה אם זו ההודעה הראשונה
        if self.is_empty:
            self.empty_label.setVisible(False)
            self.is_empty = False
        
        # הסרת המרווח
        if self.layout.count() > 0:
            stretch_item = self.layout.takeAt(self.layout.count() - 1)
        
        # הוספת ההודעה
        self.layout.addWidget(message)
        self.messages.append(message)
        
        # חיבור אות לחיצה
        message_index = len(self.messages) - 1
        message.mousePressEvent = lambda event, idx=message_index: self.message_clicked.emit(idx)
        
        # הוספת מרווח מחדש
        self.layout.addStretch()
        
        # גלילה לתחתית
        QTimer.singleShot(50, self.scroll_to_bottom)
        
        return message
    
    def scroll_to_bottom(self):
        """גלילה לתחתית הצ'אט"""
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clear_history(self):
        """ניקוי היסטוריית הצ'אט"""
        # הסרת כל ההודעות
        while self.layout.count() > 1:  # שמירה על המרווח בסוף
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # איפוס רשימת ההודעות
        self.messages = []
        
        # הצגת תווית ריקה
        self.empty_label.setVisible(True)
        self.layout.insertWidget(0, self.empty_label)
        self.is_empty = True
    
    def get_message_count(self):
        """
        מחזיר את מספר ההודעות בהיסטוריה
        
        Returns:
            int: מספר ההודעות
        """
        return len(self.messages)
    
    def get_message(self, index):
        """
        מחזיר הודעה לפי אינדקס
        
        Args:
            index (int): אינדקס ההודעה
        
        Returns:
            ChatMessage: הודעת הצ'אט המבוקשת או None אם האינדקס לא תקין
        """
        if 0 <= index < len(self.messages):
            return self.messages[index]
        return None