from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSplitter, QFrame, QScrollArea, QTextEdit, QPushButton,
                           QMessageBox, QMenu, QAction)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QDateTime, QTimer, QEvent
from PyQt6.QtGui import QFont, QCursor
import os
from ui.components.chat import ChatHistory, ChatMessage, ChatInput
from ui.components.file_upload import FileUploader, RecentFilesList, FileInfo
from services.chat_service import ChatService
from services.file_service import FileService


class HomePage(QWidget):
    """דף הבית המשלב צ'אט והעלאת קבצים"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        
        # יצירת שירותים
        self.chat_service = ChatService()
        self.file_service = FileService()
        
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
            QMenu {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #333;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #2c3e50;
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
        
        # כותרת עם תפריט
        title_layout = QHBoxLayout()
        
        title = QLabel("צ'אט")
        title.setObjectName("panelTitle")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title)
        
        # כפתור תפריט
        menu_button = QPushButton("⋮")
        menu_button.setFixedSize(30, 30)
        menu_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        menu_button.clicked.connect(self._show_chat_menu)
        title_layout.addWidget(menu_button)
        
        layout.addLayout(title_layout)
        
        # תיאור
        description = QLabel("שוחח עם ה-AI או העלה קבצי אודיו לניתוח")
        description.setStyleSheet("color: #aaa; margin-bottom: 15px;")
        layout.addWidget(description)
        
        # אזור הודעות - רכיב ChatHistory
        self.chat_history = ChatHistory()
        self.chat_history.message_clicked.connect(self.on_message_clicked)
        self.chat_history.load_more_requested.connect(self.on_load_more_messages)
        layout.addWidget(self.chat_history, 1)  # stretch factor 1
        
        # טעינת היסטוריית צ'אט
        self._load_chat_history()
        
        # אזור קלט - רכיב ChatInput
        self.chat_input = ChatInput(placeholder="הקלד הודעה כאן...")
        self.chat_input.message_sent.connect(self.on_message_sent)
        self.chat_input.typing_started.connect(self.on_typing_started)
        self.chat_input.typing_stopped.connect(self.on_typing_stopped)
        layout.addWidget(self.chat_input)
        
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
        
        # אזור העלאת קבצים
        self.file_uploader = FileUploader()
        self.file_uploader.file_upload_started.connect(self.on_file_upload_started)
        self.file_uploader.file_upload_progress.connect(self.on_file_upload_progress)
        self.file_uploader.file_upload_completed.connect(self.on_file_upload_completed)
        self.file_uploader.file_upload_failed.connect(self.on_file_upload_failed)
        layout.addWidget(self.file_uploader)
        
        # רשימת קבצים אחרונים
        self.recent_files_list = RecentFilesList(max_files=10)
        self.recent_files_list.file_selected.connect(self.on_file_selected)
        self.recent_files_list.file_play_requested.connect(self.on_file_play_requested)
        self.recent_files_list.file_delete_requested.connect(self.on_file_delete_requested)
        layout.addWidget(self.recent_files_list, 1)  # stretch factor 1
        
        # טעינת קבצים אחרונים מהמסד נתונים
        self._load_recent_files()
        
        return panel
        
    def _load_recent_files(self):
        """טעינת קבצים אחרונים מהמסד נתונים"""
        # קבלת רשימת קבצים אחרונים מהשירות
        recent_files = self.file_service.get_recent_files(limit=10)
        
        # הוספת הקבצים לרשימה
        for file_info in recent_files:
            self.recent_files_list.add_file(file_info)
    
    def _load_chat_history(self, page=1, page_size=50):
        """
        טעינת היסטוריית צ'אט
        
        Args:
            page (int, optional): מספר העמוד לטעינה (ברירת מחדל: 1)
            page_size (int, optional): גודל העמוד (מספר הודעות מקסימלי, ברירת מחדל: 50)
        """
        # טעינת סשן נוכחי
        current_session = self.chat_service.get_current_session()
        
        # אם אין סשן נוכחי, בדוק אם יש סשנים קודמים
        if current_session is None:
            sessions = self.chat_service.get_all_sessions()
            if sessions:
                # טען את הסשן האחרון
                current_session = self.chat_service.load_session(sessions[0][0], page=page, page_size=page_size)
        elif page > 1:
            # אם יש סשן נוכחי וביקשנו עמוד מסוים, טען אותו
            session_id = current_session.session_id
            current_session = self.chat_service.load_session(session_id, page=page, page_size=page_size)
        
        # אם עדיין אין סשן, צור סשן חדש
        if current_session is None:
            current_session = self.chat_service.create_session()
            # הוסף הודעת ברוכים הבאים
            self.chat_service.add_message("ברוכים הבאים ל-Audio Chat Studio! במה אוכל לעזור לך היום?", "system")
        
        # הצג את ההודעות בצ'אט
        self._display_chat_messages(current_session, page > 1)
    
    def _display_chat_messages(self, session, append=False):
        """
        הצגת הודעות צ'אט מסשן
        
        Args:
            session (ChatSession): סשן הצ'אט להצגה
            append (bool, optional): האם להוסיף את ההודעות לקיימות או להחליף אותן
        """
        # אם לא מוסיפים הודעות, נקה את ההיסטוריה
        if not append:
            self.chat_history.clear_history(confirm=False)
        
        # הגדרת מידע על עימוד
        if hasattr(session, 'pagination'):
            self.chat_history.set_pagination(session.pagination)
        
        # הוספת הודעות מהסשן
        for message in session.messages:
            timestamp = QDateTime.fromString(message.timestamp.isoformat(), Qt.DateFormat.ISODate)
            
            if message.sender == "user":
                self.chat_history.add_user_message(message.text, timestamp)
            elif message.sender == "ai":
                self.chat_history.add_ai_message(message.text, timestamp)
            elif message.sender == "system":
                self.chat_history.add_system_message(message.text, timestamp)
        
        # אם מוסיפים הודעות, גלול למיקום הנוכחי
        if append:
            # שמירת המיקום הנוכחי
            current_position = self.chat_history.verticalScrollBar().value()
            # גלילה למיקום הנוכחי אחרי הוספת ההודעות
            QTimer.singleShot(50, lambda: self.chat_history.verticalScrollBar().setValue(current_position))
    
    def _show_chat_menu(self):
        """הצגת תפריט צ'אט"""
        menu = QMenu(self)
        
        # פעולות תפריט
        new_chat_action = QAction("שיחה חדשה", self)
        new_chat_action.triggered.connect(self._new_chat)
        menu.addAction(new_chat_action)
        
        clear_chat_action = QAction("נקה שיחה נוכחית", self)
        clear_chat_action.triggered.connect(self._clear_chat)
        menu.addAction(clear_chat_action)
        
        # הוספת מפריד
        menu.addSeparator()
        
        # טעינת סשנים קודמים
        sessions = self.chat_service.get_all_sessions()
        if sessions:
            load_menu = QMenu("טען שיחה", self)
            menu.addMenu(load_menu)
            
            for session_id, title, updated_at in sessions:
                # הצגת תאריך בפורמט קריא
                date_str = updated_at.strftime("%d/%m/%Y %H:%M")
                action = QAction(f"{title} ({date_str})", self)
                action.triggered.connect(lambda checked, sid=session_id: self._load_chat_session(sid))
                load_menu.addAction(action)
        
        # הצגת התפריט
        menu.exec(QCursor.pos())
    
    def _new_chat(self):
        """יצירת שיחה חדשה"""
        # יצירת סשן חדש
        session = self.chat_service.create_session()
        
        # הוספת הודעת ברוכים הבאים
        self.chat_service.add_message("ברוכים הבאים ל-Audio Chat Studio! במה אוכל לעזור לך היום?", "system")
        
        # הצגת הודעות
        self._display_chat_messages(session)
    
    def _clear_chat(self):
        """ניקוי שיחה נוכחית"""
        # ניקוי היסטוריית צ'אט עם אישור
        if self.chat_history.clear_history(confirm=True):
            # ניקוי הסשן הנוכחי
            self.chat_service.clear_current_session()
            
            # הוספת הודעת ברוכים הבאים
            welcome_msg = "השיחה נוקתה. במה אוכל לעזור לך?"
            self.chat_service.add_message(welcome_msg, "system")
            self.chat_history.add_system_message(welcome_msg)
    
    def _load_chat_session(self, session_id):
        """טעינת סשן צ'אט"""
        # טעינת הסשן
        session = self.chat_service.load_session(session_id)
        
        if session:
            # הצגת הודעות
            self._display_chat_messages(session)
    
    def on_message_sent(self, text):
        """טיפול בשליחת הודעה מהמשתמש"""
        if text:
            # הוספת הודעת משתמש לשירות הצ'אט
            self.chat_service.add_message(text, "user")
            
            # הוספת הודעת משתמש לממשק
            self.chat_history.add_user_message(text)
            
            # סימולציה של תשובת AI
            self._simulate_ai_response(text)
    
    def on_typing_started(self):
        """טיפול בהתחלת הקלדה"""
        # כאן ניתן להוסיף לוגיקה כמו הצגת "המשתמש מקליד..."
        pass
    
    def on_typing_stopped(self):
        """טיפול בסיום הקלדה"""
        # כאן ניתן להוסיף לוגיקה כמו הסתרת "המשתמש מקליד..."
        pass
    
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
        QTimer.singleShot(800, lambda: self._add_ai_response(response))
    
    def on_message_clicked(self, message_index):
        """טיפול בלחיצה על הודעה"""
        message = self.chat_history.get_message(message_index)
        if message:
            print(f"נלחצה הודעה: {message.text}")
    
    def on_load_more_messages(self):
        """טיפול בבקשה לטעינת הודעות נוספות"""
        # קבלת מידע על עימוד נוכחי
        current_page = self.chat_history.pagination["page"]
        page_size = self.chat_history.pagination["page_size"]
        
        # טעינת העמוד הקודם
        if current_page > 1:
            self._load_chat_history(page=current_page - 1, page_size=page_size)
  def on_file_upload_started(self, file_path):
        """טיפול בהתחלת העלאת קובץ"""
        self.chat_history.add_system_message(f"מתחיל להעלות את הקובץ: {os.path.basename(file_path)}")
    
    def on_file_upload_progress(self, file_path, progress):
        """טיפול בהתקדמות העלאת קובץ"""
        # אפשר להוסיף כאן לוגיקה להצגת התקדמות העלאה
        pass
    
    def on_file_upload_completed(self, file_info):
        """טיפול בסיום העלאת קובץ"""
        # שמירת מידע על הקובץ במסד הנתונים
        self.file_service.save_file_info(file_info)
        
        # הוספת הקובץ לרשימת הקבצים האחרונים
        self.recent_files_list.add_file(file_info)
        
        # הודעה בצ'אט
        system_msg = f"הקובץ {file_info.name} הועלה בהצלחה"
        self.chat_service.add_message(system_msg, "system")
        self.chat_history.add_system_message(system_msg)
        
        # הצעת פעולות על הקובץ
        ai_msg = (f"הקובץ {file_info.name} הועלה בהצלחה. מה תרצה לעשות עם הקובץ?\n\n"
                 f"- ניתוח הקובץ\n"
                 f"- תמלול הקובץ\n"
                 f"- עריכת הקובץ (הסרת רעשים, חיתוך, וכו')\n"
                 f"- המרה לפורמט אחר")
        QTimer.singleShot(1000, lambda: self._add_ai_response(ai_msg))
    
    def on_file_upload_failed(self, file_path, error):
        """טיפול בכישלון העלאת קובץ"""
        file_name = os.path.basename(file_path)
        system_msg = f"העלאת הקובץ {file_name} נכשלה: {error}"
        self.chat_service.add_message(system_msg, "system")
        self.chat_history.add_system_message(system_msg)
    
    def on_file_selected(self, file_info):
        """טיפול בבחירת קובץ מהרשימה"""
        system_msg = f"נבחר הקובץ: {file_info.name}"
        self.chat_service.add_message(system_msg, "system")
        self.chat_history.add_system_message(system_msg)
        
        # הצעת פעולות על הקובץ
        ai_msg = (f"מה תרצה לעשות עם הקובץ {file_info.name}?\n\n"
                 f"- ניתוח הקובץ\n"
                 f"- תמלול הקובץ\n"
                 f"- עריכת הקובץ (הסרת רעשים, חיתוך, וכו')\n"
                 f"- המרה לפורמט אחר")
        QTimer.singleShot(500, lambda: self._add_ai_response(ai_msg))
    
    def on_file_play_requested(self, file_info):
        """טיפול בבקשה לנגן קובץ"""
        system_msg = f"מנגן את הקובץ: {file_info.name}"
        self.chat_service.add_message(system_msg, "system")
        self.chat_history.add_system_message(system_msg)
        
        # כאן היינו מוסיפים קוד לנגינת הקובץ
        # לדוגמה:
        # self.audio_player.play(file_info.path)
    
    def on_file_delete_requested(self, file_info):
        """טיפול בבקשה למחוק קובץ"""
        # שאלת אישור
        reply = QMessageBox.question(
            self,
            "אישור מחיקה",
            f"האם אתה בטוח שברצונך למחוק את הקובץ {file_info.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # מחיקת הקובץ ממסד הנתונים
            self.file_service.delete_file(file_info.path)
            
            # בפרויקט אמיתי, כאן היינו מוחקים את הקובץ מהשרת או מהדיסק
            # os.remove(file_info.path)
            
            # הסרת הקובץ מהרשימה
            self.recent_files_list.remove_file(file_info)
            
            # הודעה בצ'אט
            system_msg = f"הקובץ {file_info.name} נמחק בהצלחה"
            self.chat_service.add_message(system_msg, "system")
            self.chat_history.add_system_message(system_msg)    def
 _add_ai_response(self, text):
        """הוספת תשובת AI לצ'אט ולשירות"""
        # הוספת הודעת AI לשירות הצ'אט
        self.chat_service.add_message(text, "ai")
        
        # הוספת הודעת AI לממשק
        self.chat_history.add_ai_message(text)