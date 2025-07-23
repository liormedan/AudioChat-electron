from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSplitter, QFrame, QScrollArea, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QDateTime, QTimer, QEvent
from PyQt6.QtGui import QFont
from ui.components.chat import ChatHistory, ChatMessage


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
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        try:
            self.splitter = QSplitter(Qt.Horizontal)
        except AttributeError:
            try:
                self.splitter = QSplitter(Qt.Orientation.Horizontal)
            except AttributeError:
                # אם שום דבר לא עובד, נשתמש בערכים מספריים
                self.splitter = QSplitter(1)  # Horizontal = 1
        self.splitter.addWidget(self.chat_panel)
        self.splitter.addWidget(self.file_panel)
        
        # הגדרת גדלים התחלתיים (60% לצ'אט, 40% לקבצים)
        self.splitter.setSizes([600, 400])
        
        self.main_layout.addWidget(self.splitter)
    
    def _create_chat_panel(self):
        """יצירת פאנל צ'אט"""
        panel = QFrame()
        panel.setObjectName("chatPanel")
        # panel.setFrameShape(QFrame.StyledPanel)  # מבוטל בגלל בעיית תאימות
        
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
        
        # אזור הודעות - רכיב ChatHistory
        self.chat_history = ChatHistory()
        self.chat_history.message_clicked.connect(self.on_message_clicked)
        layout.addWidget(self.chat_history, 1)  # stretch factor 1
        
        # הוספת הודעות דוגמה
        self._add_sample_messages()
        
        # אזור קלט
        input_layout = QHBoxLayout()
        
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("הקלד הודעה...")
        self.chat_input.setMaximumHeight(80)
        self.chat_input.installEventFilter(self)  # התקנת מסנן אירועים לתפיסת מקש Enter
        input_layout.addWidget(self.chat_input)
        
        self.send_button = QPushButton("שלח")
        self.send_button.setMinimumWidth(80)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        return panel
    
    def _create_file_panel(self):
        """יצירת פאנל העלאת קבצים"""
        panel = QFrame()
        panel.setObjectName("filePanel")
        # panel.setFrameShape(QFrame.StyledPanel)  # מבוטל בגלל בעיית תאימות
        
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
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        try:
            upload_area.setAlignment(Qt.AlignCenter)
        except AttributeError:
            try:
                upload_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except AttributeError:
                # אם שום דבר לא עובד, נשתמש בערכים מספריים
                upload_area.setAlignment(0x0004 | 0x0080)  # AlignCenter = AlignHCenter | AlignVCenter
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
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        try:
            recent_files_layout.setAlignment(Qt.AlignTop)
        except AttributeError:
            try:
                recent_files_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            except AttributeError:
                # אם שום דבר לא עובד, נשתמש בערכים מספריים
                recent_files_layout.setAlignment(0x0001)  # AlignTop = 0x0001
        recent_files_layout.addWidget(QLabel("אין קבצים אחרונים להצגה"))
        
        recent_files_area.setWidget(recent_files_content)
        layout.addWidget(recent_files_area, 1)  # stretch factor 1
        
        return panel
    
    def _add_sample_messages(self):
        """הוספת הודעות דוגמה לצ'אט"""
        # יצירת הודעות עם תאריכים שונים
        yesterday = QDateTime.currentDateTime().addDays(-1)
        
        # הודעת ברוכים הבאים
        self.chat_history.add_system_message("ברוכים הבאים ל-Audio Chat Studio! במה אוכל לעזור לך היום?")
        
        # הודעות דוגמה מאתמול
        self.chat_history.add_user_message("אני רוצה לערוך קובץ אודיו", yesterday)
        self.chat_history.add_ai_message("בשמחה! תוכל להעלות קובץ אודיו ואעזור לך לערוך אותו. אילו שינויים תרצה לבצע?", yesterday)
        self.chat_history.add_user_message("אני רוצה להסיר רעשי רקע", yesterday)
        self.chat_history.add_ai_message("אוכל לעזור לך להסיר רעשי רקע. העלה את הקובץ ואשתמש באלגוריתם לסינון רעשים.", yesterday)
        
        # הודעות דוגמה מהיום
        self.chat_history.add_user_message("האם אתה יכול לתמלל קובץ אודיו?")
        self.chat_history.add_ai_message("כן, אני יכול לתמלל קבצי אודיו. פשוט העלה את הקובץ ואשתמש במודל תמלול מתקדם כדי להמיר את האודיו לטקסט. האם תרצה לנסות זאת עכשיו?")
    
    def eventFilter(self, obj, event):
        """סינון אירועים לתפיסת מקש Enter"""
        # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
        key_press_event = None
        try:
            key_press_event = QEvent.KeyPress
        except AttributeError:
            try:
                key_press_event = QEvent.Type.KeyPress
            except AttributeError:
                key_press_event = 6  # KeyPress = 6
                
        if obj is self.chat_input and event.type() == key_press_event:
            # בגרסאות שונות של PyQt6 יש שמות שונים לקבועים
            key_return = None
            shift_modifier = None
            try:
                key_return = Qt.Key_Return
                shift_modifier = Qt.ShiftModifier
            except AttributeError:
                try:
                    key_return = Qt.Key.Key_Return
                    shift_modifier = Qt.KeyboardModifier.ShiftModifier
                except AttributeError:
                    key_return = 0x01000004  # Key_Return = 0x01000004
                    shift_modifier = 0x02000000  # ShiftModifier = 0x02000000
                    
            if event.key() == key_return and not event.modifiers() & shift_modifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def send_message(self):
        """שליחת הודעה מהמשתמש"""
        text = self.chat_input.toPlainText().strip()
        if text:
            # הוספת הודעת משתמש
            self.chat_history.add_user_message(text)
            
            # ניקוי תיבת הקלט
            self.chat_input.clear()
            
            # סימולציה של תשובת AI
            self._simulate_ai_response(text)
    
    def _simulate_ai_response(self, user_text):
        """סימולציה של תשובת AI"""
        # תשובות פשוטות לפי תוכן ההודעה
        if "שלום" in user_text or "היי" in user_text:
            response = "שלום! איך אני יכול לעזור לך היום?"
        elif "תודה" in user_text:
            response = "בשמחה! אם תצטרך עזרה נוספת, אני כאן."
        elif "אודיו" in user_text or "קובץ" in user_text or "קבצים" in user_text:
            response = "אני יכול לעזור לך עם קבצי אודיו. תוכל להעלות קובץ דרך הפאנל בצד ימין, ואוכל לעזור לך לערוך, לתמלל או לנתח אותו."
        elif "עריכה" in user_text or "לערוך" in user_text:
            response = "יש לי מגוון כלי עריכה לקבצי אודיו, כולל הסרת רעשים, חיתוך, שינוי מהירות, והוספת אפקטים. מה תרצה לעשות?"
        elif "תמלול" in user_text or "לתמלל" in user_text:
            response = "אני יכול לתמלל קבצי אודיו למגוון שפות. פשוט העלה את הקובץ ואתחיל בתמלול."
        else:
            response = "אני מבין. האם תרצה להעלות קובץ אודיו כדי שאוכל לעזור לך לעבוד עליו?"
        
        # הוספת תשובת AI אחרי השהייה קצרה
        QTimer.singleShot(800, lambda: self.chat_history.add_ai_message(response))
    
    def on_message_clicked(self, message_index):
        """טיפול בלחיצה על הודעה"""
        message = self.chat_history.get_message(message_index)
        if message:
            print(f"נלחצה הודעה: {message.text}")