from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal
from .chat_message import ChatMessage


class ChatHistory(QScrollArea):
    """רכיב להצגת היסטוריית צ'אט"""
    
    # אותות
    message_clicked = pyqtSignal(int)  # אות שנשלח כאשר לוחצים על הודעה
    load_more_requested = pyqtSignal()  # אות שנשלח כאשר המשתמש מבקש לטעון עוד הודעות
    file_attachment_clicked = pyqtSignal(dict)  # אות שנשלח כאשר לוחצים על קובץ מצורף
    
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
        
        # כפתור "טען עוד"
        self.load_more_button = QPushButton("טען הודעות קודמות")
        self.load_more_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        self.load_more_button.clicked.connect(self.on_load_more_clicked)
        self.load_more_button.setVisible(False)
        self.layout.addWidget(self.load_more_button)
        
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
        
        # מידע על עימוד
        self.pagination = {
            "page": 1,
            "page_size": 50,
            "total_messages": 0,
            "total_pages": 1
        }
        
        # חיבור אירוע גלילה לבדיקת הגעה לראש הצ'אט
        self.verticalScrollBar().valueChanged.connect(self.check_scroll_position)
    
    def check_scroll_position(self, value):
        """בדיקת מיקום הגלילה והצגת כפתור 'טען עוד' בהתאם"""
        # אם הגענו לראש הצ'אט ויש עוד הודעות לטעון
        if value == 0 and self.pagination["page"] < self.pagination["total_pages"]:
            self.load_more_button.setVisible(True)
        else:
            self.load_more_button.setVisible(False)
    
    def on_load_more_clicked(self):
        """טיפול בלחיצה על כפתור 'טען עוד'"""
        # שליחת אות לטעינת עוד הודעות
        self.load_more_requested.emit()
        
    def set_pagination(self, pagination_data):
        """
        הגדרת מידע על עימוד
        
        Args:
            pagination_data (dict): מידע על עימוד
        """
        self.pagination = pagination_data
        
        # הצגת כפתור 'טען עוד' אם יש עוד עמודים
        if self.pagination["page"] < self.pagination["total_pages"]:
            self.load_more_button.setVisible(True)
        else:
            self.load_more_button.setVisible(False)
    
    def add_user_message(self, text, timestamp=None, attachments=None):
        """
        הוספת הודעת משתמש
        
        Args:
            text (str): תוכן ההודעה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
            attachments (list, optional): רשימת קבצים מצורפים
        
        Returns:
            ChatMessage: הודעת הצ'אט שנוצרה
        """
        message = ChatMessage(text, "user", timestamp=timestamp, attachments=attachments)
        return self._add_message(message)
    
    def add_ai_message(self, text, timestamp=None, attachments=None):
        """
        הוספת הודעת AI
        
        Args:
            text (str): תוכן ההודעה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
            attachments (list, optional): רשימת קבצים מצורפים
        
        Returns:
            ChatMessage: הודעת הצ'אט שנוצרה
        """
        message = ChatMessage(text, "ai", timestamp=timestamp, attachments=attachments)
        return self._add_message(message)
    
    def add_system_message(self, text, timestamp=None, attachments=None):
        """
        הוספת הודעת מערכת
        
        Args:
            text (str): תוכן ההודעה
            timestamp (QDateTime, optional): זמן שליחת ההודעה
            attachments (list, optional): רשימת קבצים מצורפים
        
        Returns:
            ChatMessage: הודעת הצ'אט שנוצרה
        """
        message = ChatMessage(text, "system", timestamp=timestamp, attachments=attachments)
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
        
        # חיבור אות לחיצה על קובץ מצורף
        message.file_clicked.connect(self.on_file_attachment_clicked)
        
        # הוספת מרווח מחדש
        self.layout.addStretch()
        
        # גלילה לתחתית
        QTimer.singleShot(50, self.scroll_to_bottom)
        
        return message
        
    def on_file_attachment_clicked(self, attachment):
        """
        טיפול בלחיצה על קובץ מצורף
        
        Args:
            attachment (dict): מידע על הקובץ המצורף
        """
        # כאן אנחנו יכולים להעביר את האירוע לרכיב ההורה
        # לדוגמה, אם היינו מוסיפים אות file_attachment_clicked
        # היינו יכולים לשלוח אותו כך:
        # self.file_attachment_clicked.emit(attachment)
        
        # כרגע נדפיס את המידע על הקובץ
        print(f"נלחץ קובץ מצורף: {attachment.get('name', 'קובץ לא ידוע')}")
    
    def scroll_to_bottom(self):
        """גלילה לתחתית הצ'אט"""
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clear_history(self, confirm=True):
        """
        ניקוי היסטוריית הצ'אט
        
        Args:
            confirm (bool, optional): האם להציג דיאלוג אישור
        
        Returns:
            bool: האם הניקוי בוצע
        """
        if confirm:
            # הצגת דיאלוג אישור
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "אישור ניקוי היסטוריה",
                "האם אתה בטוח שברצונך לנקות את היסטוריית הצ'אט?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return False
        
        # הסרת כל ההודעות
        for message in self.messages:
            if message in self.messages and message.parent() == self.container:
                message.setParent(None)
                message.deleteLater()
        
        # איפוס רשימת ההודעות
        self.messages = []
        
        # הצגת תווית ריקה
        self.is_empty = True
        
        # הסתרת כפתור 'טען עוד'
        self.load_more_button.setVisible(False)
        
        # איפוס מידע על עימוד
        self.pagination = {
            "page": 1,
            "page_size": 50,
            "total_messages": 0,
            "total_pages": 1
        }
        
        return True
    
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