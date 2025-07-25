from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSplitter, QFrame, QScrollArea, QTextEdit, QPushButton,
                           QMessageBox, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QDateTime, QTimer, QEvent
from PyQt6.QtGui import QFont, QCursor, QIcon, QAction
import os
from ui.components.chat import ChatHistory, ChatMessage, ChatInput
from ui.components.file_upload import FileUploader, RecentFilesList, FileInfo
from app_context import chat_service, llm_service, settings_service
from services.file_service import FileService


class HomePage(QWidget):
    """דף הבית המשלב צ'אט והעלאת קבצים"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        
        # יצירת שירותים
        self.chat_service = chat_service
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
        self.chat_input.file_reference_requested.connect(self.on_file_reference_requested)
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
            # הוסף הודעת ברוכים הבאים מורחבת
            welcome_message = (
                "ברוכים הבאים ל-Audio Chat Studio! 🎵\n\n"
                "אני כאן כדי לעזור לך עם קבצי האודיו שלך. הנה כמה דברים שאני יכול לעשות:\n\n"
                "• **העלאת קבצים** - השתמש בפאנל הימני כדי להעלות קבצי אודיו\n"
                "• **ניתוח קבצים** - אוכל לנתח את הקבצים שלך ולספק מידע מפורט\n"
                "• **תמלול** - אוכל לתמלל את תוכן הקבצים שלך\n"
                "• **עריכה** - אוכל להציע כלים לעריכת הקבצים שלך\n\n"
                "כדי להתחיל, פשוט העלה קובץ או שאל אותי שאלה!"
            )
            self.chat_service.add_message(welcome_message, "system")
        
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
            
            ai_text = self.chat_service.generate_ai_reply(text)
            if ai_text:
                self.chat_history.add_ai_message(ai_text)
            else:
                self._simulate_ai_response(text)
    
    def on_typing_started(self):
        """טיפול בהתחלת הקלדה"""
        # כאן ניתן להוסיף לוגיקה כמו הצגת "המשתמש מקליד..."
        pass
    
    def on_typing_stopped(self):
        """טיפול בסיום הקלדה"""
        # כאן ניתן להוסיף לוגיקה כמו הסתרת "המשתמש מקליד..."
        pass
        
    def on_file_reference_requested(self):
        """טיפול בבקשה להוספת התייחסות לקובץ"""
        # קבלת רשימת קבצים אחרונים
        recent_files = self.file_service.get_recent_files(limit=5)
        
        if not recent_files:
            # אם אין קבצים אחרונים, הצג הודעה בצ'אט
            self.chat_history.add_system_message("אין קבצים אחרונים להתייחסות. העלה קובץ קודם.")
            return
        
        # יצירת תפריט עם הקבצים האחרונים
        menu = QMenu(self)
        menu.setStyleSheet("""
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
        
        # הוספת כותרת
        title_action = QAction("בחר קובץ להתייחסות:", self)
        title_action.setEnabled(False)
        menu.addAction(title_action)
        menu.addSeparator()
        
        # הוספת הקבצים האחרונים
        for file_info in recent_files:
            action = QAction(file_info.name, self)
            action.triggered.connect(lambda checked=False, f=file_info: self.chat_input.insert_file_reference(f))
            menu.addAction(action)
        
        # הצגת התפריט
        menu.exec(QCursor.pos())
    
    def _simulate_ai_response(self, user_text):
        """סימולציה של תשובת AI"""
        # בדיקה אם יש התייחסות לקובץ בהודעה
        file_reference = None
        if "[קובץ:" in user_text and "]" in user_text:
            start_idx = user_text.find("[קובץ:") + 6
            end_idx = user_text.find("]", start_idx)
            if start_idx > 6 and end_idx > start_idx:
                file_name = user_text[start_idx:end_idx].strip()
                # חיפוש הקובץ במסד הנתונים
                recent_files = self.file_service.get_recent_files(limit=10)
                for file_info in recent_files:
                    if file_info.name == file_name:
                        file_reference = file_info
                        break
        
        # תשובות לפי תוכן ההודעה והקובץ המצורף
        if file_reference:
            # אם יש התייחסות לקובץ, נתח אותו
            response = self._analyze_audio_file(file_reference, user_text)
        elif "שלום" in user_text or "היי" in user_text:
            response = "שלום! איך אני יכול לעזור לך היום?"
        elif "תודה" in user_text:
            response = "בשמחה! אם תצטרך עזרה נוספת, אני כאן."
        elif "אודיו" in user_text or "קובץ" in user_text or "קבצים" in user_text:
            response = "אני יכול לעזור לך עם קבצי אודיו. תוכל להעלות קובץ דרך הפאנל בצד ימין, ואוכל לעזור לך לערוך, לתמלל או לנתח אותו."
        elif "עריכה" in user_text or "לערוך" in user_text:
            response = "יש לי מגוון כלי עריכה לקבצי אודיו, כולל הסרת רעשים, חיתוך, שינוי מהירות, והוספת אפקטים. מה תרצה לעשות?"
        elif "תמלול" in user_text or "לתמלל" in user_text:
            response = "אני יכול לתמלל קבצי אודיו למגוון שפות. פשוט העלה את הקובץ ואתחיל בתמלול."
        elif "ניתוח" in user_text or "לנתח" in user_text:
            response = "אני יכול לנתח קבצי אודיו ולספק מידע על איכות הקול, עוצמה, תדרים ועוד. העלה קובץ או התייחס לקובץ קיים כדי שאוכל לנתח אותו."
        else:
            response = "אני מבין. האם תרצה להעלות קובץ אודיו כדי שאוכל לעזור לך לעבוד עליו?"
        
        # הוספת תשובת AI אחרי השהייה קצרה
        QTimer.singleShot(800, lambda: self._add_ai_response(response))
    
    def _analyze_audio_file(self, file_info, user_text):
        """
        ניתוח קובץ אודיו והחזרת תשובה מתאימה
        
        Args:
            file_info: מידע על הקובץ לניתוח
            user_text: טקסט ההודעה של המשתמש
            
        Returns:
            str: תשובת AI מבוססת על הניתוח
        """
        # בדיקה מה המשתמש רוצה לעשות עם הקובץ
        if "נתח" in user_text or "ניתוח" in user_text or "אנליזה" in user_text:
            # ניתוח הקובץ
            return self._generate_audio_analysis(file_info)
        elif "תמלל" in user_text or "תמלול" in user_text:
            # תמלול הקובץ
            return f"אני מתחיל בתמלול הקובץ {file_info.name}. תהליך התמלול עשוי לקחת מספר דקות, בהתאם לאורך הקובץ.\n\nאעדכן אותך כשהתמלול יהיה מוכן."
        elif "ערוך" in user_text or "עריכה" in user_text:
            # עריכת הקובץ
            return f"אילו פעולות עריכה תרצה לבצע על הקובץ {file_info.name}?\n\n- הסרת רעשי רקע\n- חיתוך הקובץ\n- שינוי עוצמת הקול\n- הוספת אפקטים\n- שינוי קצב הנגינה"
        elif "המר" in user_text or "המרה" in user_text:
            # המרת פורמט
            return f"לאיזה פורמט תרצה להמיר את הקובץ {file_info.name}?\n\n- MP3\n- WAV\n- FLAC\n- OGG\n- M4A"
        else:
            # תשובה כללית
            return f"אני רואה שאתה מתייחס לקובץ {file_info.name}. זהו קובץ {file_info.format.upper()} באורך {file_info.duration_formatted}. מה תרצה לעשות עם הקובץ?\n\n- ניתוח הקובץ\n- תמלול הקובץ\n- עריכת הקובץ\n- המרת פורמט"
    
    def _generate_audio_analysis(self, file_info):
        """
        יצירת ניתוח מדומה לקובץ אודיו
        
        Args:
            file_info: מידע על הקובץ לניתוח
            
        Returns:
            str: ניתוח מדומה של הקובץ
        """
        # בפרויקט אמיתי, כאן היינו מנתחים את הקובץ באמת
        # כרגע נחזיר ניתוח מדומה
        
        # יצירת ערכים מדומים
        import random
        
        # ערכים מדומים לניתוח
        sample_rate = random.choice([44100, 48000, 96000])
        bit_depth = random.choice([16, 24, 32])
        channels = random.choice([1, 2])
        bitrate = random.choice([128, 192, 256, 320])
        
        # יצירת הניתוח
        analysis = f"# ניתוח הקובץ {file_info.name}\n\n"
        analysis += f"## מידע בסיסי\n"
        analysis += f"- **פורמט**: {file_info.format.upper()}\n"
        analysis += f"- **גודל**: {file_info.size_formatted}\n"
        
        if file_info.duration > 0:
            analysis += f"- **אורך**: {file_info.duration_formatted}\n"
        
        analysis += f"- **תאריך העלאה**: {file_info.upload_date_formatted}\n\n"
        
        analysis += f"## מידע טכני\n"
        analysis += f"- **קצב דגימה**: {sample_rate} Hz\n"
        analysis += f"- **עומק סיביות**: {bit_depth} bit\n"
        analysis += f"- **ערוצים**: {channels} ({'מונו' if channels == 1 else 'סטריאו'})\n"
        
        if file_info.format.lower() in ['mp3', 'ogg', 'm4a', 'aac']:
            analysis += f"- **קצב סיביות**: {bitrate} kbps\n\n"
        
        analysis += f"## איכות הקול\n"
        
        # איכות מדומה בהתאם לפורמט
        if file_info.format.lower() in ['wav', 'flac']:
            quality = "גבוהה"
            dynamic_range = random.uniform(60, 90)
            noise_level = random.uniform(-80, -60)
        else:
            quality = "בינונית"
            dynamic_range = random.uniform(40, 60)
            noise_level = random.uniform(-60, -40)
        
        analysis += f"- **איכות כללית**: {quality}\n"
        analysis += f"- **טווח דינמי**: {dynamic_range:.1f} dB\n"
        analysis += f"- **רמת רעש**: {noise_level:.1f} dB\n\n"
        
        analysis += f"## המלצות\n"
        
        # המלצות בהתאם לפורמט ולאיכות
        if file_info.format.lower() in ['mp3', 'ogg', 'm4a'] and bitrate < 256:
            analysis += f"- שקול להשתמש בקצב סיביות גבוה יותר לאיכות טובה יותר\n"
        
        if noise_level > -60:
            analysis += f"- הקובץ מכיל רמת רעש גבוהה יחסית, מומלץ להשתמש בכלי להפחתת רעשים\n"
        
        if file_info.duration > 300:  # אם הקובץ ארוך מ-5 דקות
            analysis += f"- הקובץ ארוך יחסית, שקול לחלק אותו לקטעים קצרים יותר לעבודה יעילה יותר\n"
        
        return analysis
    
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
        
        # הודעה בצ'אט עם קובץ מצורף
        system_msg = f"הקובץ {file_info.name} הועלה בהצלחה"
        
        # יצירת מידע על הקובץ המצורף
        attachment = {
            "type": "audio_file",
            "name": file_info.name,
            "path": file_info.path,
            "size": file_info.size,
            "format": file_info.format,
            "duration": file_info.duration,
            "upload_date": file_info.upload_date.isoformat() if hasattr(file_info.upload_date, 'isoformat') else str(file_info.upload_date)
        }
        
        # הוספת הודעה עם קובץ מצורף
        self.chat_service.add_message(system_msg, "system", file_info)
        self.chat_history.add_system_message(system_msg, attachments=[attachment])
        
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
        
        # יצירת מידע על הקובץ המצורף
        attachment = {
            "type": "audio_file",
            "name": file_info.name,
            "path": file_info.path,
            "size": file_info.size,
            "format": file_info.format,
            "duration": file_info.duration,
            "upload_date": file_info.upload_date.isoformat() if hasattr(file_info.upload_date, 'isoformat') else str(file_info.upload_date)
        }
        
        # הוספת הודעה עם קובץ מצורף
        self.chat_service.add_message(system_msg, "system", file_info)
        self.chat_history.add_system_message(system_msg, attachments=[attachment])
        
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
            self.chat_history.add_system_message(system_msg)
    
    def _add_ai_response(self, text):
        """הוספת תשובת AI לצ'אט ולשירות"""
        # הוספת הודעת AI לשירות הצ'אט
        self.chat_service.add_message(text, "ai")
        
        # הוספת הודעת AI לממשק
        self.chat_history.add_ai_message(text)
