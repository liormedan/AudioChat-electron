import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from PyQt6.QtCore import QObject, pyqtSignal


class ChatMessage:
    """מודל להודעת צ'אט"""
    
    def __init__(self, text: str, sender: str, timestamp: Optional[datetime] = None):
        """
        יוצר הודעת צ'אט חדשה
        
        Args:
            text (str): תוכן ההודעה
            sender (str): שולח ההודעה ("user", "ai", או "system")
            timestamp (datetime, optional): זמן שליחת ההודעה
        """
        self.text = text
        self.sender = sender
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת ההודעה למילון"""
        return {
            "text": self.text,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """יצירת הודעה ממילון"""
        return cls(
            text=data["text"],
            sender=data["sender"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class ChatSession:
    """מודל לסשן צ'אט"""
    
    def __init__(self, session_id: str, title: str, messages: List[ChatMessage] = None):
        """
        יוצר סשן צ'אט חדש
        
        Args:
            session_id (str): מזהה הסשן
            title (str): כותרת הסשן
            messages (List[ChatMessage], optional): רשימת הודעות
        """
        self.session_id = session_id
        self.title = title
        self.messages = messages or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_message(self, message: ChatMessage) -> None:
        """הוספת הודעה לסשן"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת הסשן למילון"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "messages": [message.to_dict() for message in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """יצירת סשן ממילון"""
        session = cls(
            session_id=data["session_id"],
            title=data["title"],
            messages=[ChatMessage.from_dict(msg) for msg in data["messages"]]
        )
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.updated_at = datetime.fromisoformat(data["updated_at"])
        return session


class ChatService(QObject):
    """שירות לניהול צ'אטים"""
    
    # אותות
    session_loaded = pyqtSignal(object)  # אות שנשלח כאשר נטען סשן
    session_saved = pyqtSignal(str)  # אות שנשלח כאשר נשמר סשן
    session_deleted = pyqtSignal(str)  # אות שנשלח כאשר נמחק סשן
    
    def __init__(self, db_path: str = None):
        """
        יוצר שירות צ'אט חדש
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים
        """
        super().__init__()
        
        # נתיב למסד הנתונים
        if db_path is None:
            # נתיב ברירת מחדל
            app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, "chat_history.db")
        
        self.db_path = db_path
        
        # יצירת מסד נתונים אם לא קיים
        self._init_db()
        
        # סשן נוכחי
        self.current_session = None
    
    def _init_db(self) -> None:
        """יצירת מסד נתונים אם לא קיים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # יצירת טבלת סשנים
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            data TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, title: str = "שיחה חדשה") -> ChatSession:
        """
        יצירת סשן חדש
        
        Args:
            title (str, optional): כותרת הסשן
        
        Returns:
            ChatSession: הסשן החדש
        """
        # יצירת מזהה סשן
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # יצירת סשן
        session = ChatSession(session_id=session_id, title=title)
        
        # שמירת הסשן
        self._save_session(session)
        
        # הגדרת הסשן הנוכחי
        self.current_session = session
        
        return session
    
    def _save_session(self, session: ChatSession) -> None:
        """
        שמירת סשן במסד הנתונים
        
        Args:
            session (ChatSession): הסשן לשמירה
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # המרת הסשן למילון ואז ל-JSON
        session_data = json.dumps(session.to_dict())
        
        # שמירת הסשן
        cursor.execute('''
        INSERT OR REPLACE INTO chat_sessions (session_id, title, created_at, updated_at, data)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            session.session_id,
            session.title,
            session.created_at.isoformat(),
            session.updated_at.isoformat(),
            session_data
        ))
        
        conn.commit()
        conn.close()
        
        # שליחת אות
        self.session_saved.emit(session.session_id)
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """
        טעינת סשן ממסד הנתונים
        
        Args:
            session_id (str): מזהה הסשן
        
        Returns:
            Optional[ChatSession]: הסשן שנטען, או None אם לא נמצא
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טעינת הסשן
        cursor.execute('''
        SELECT data FROM chat_sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        # המרת ה-JSON למילון ואז לסשן
        session_data = json.loads(row[0])
        session = ChatSession.from_dict(session_data)
        
        # הגדרת הסשן הנוכחי
        self.current_session = session
        
        # שליחת אות
        self.session_loaded.emit(session)
        
        return session
    
    def get_all_sessions(self) -> List[Tuple[str, str, datetime]]:
        """
        קבלת כל הסשנים
        
        Returns:
            List[Tuple[str, str, datetime]]: רשימת סשנים (מזהה, כותרת, תאריך עדכון)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טעינת כל הסשנים
        cursor.execute('''
        SELECT session_id, title, updated_at FROM chat_sessions
        ORDER BY updated_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # המרת התאריכים
        sessions = []
        for row in rows:
            session_id, title, updated_at = row
            sessions.append((session_id, title, datetime.fromisoformat(updated_at)))
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        מחיקת סשן
        
        Args:
            session_id (str): מזהה הסשן
        
        Returns:
            bool: האם המחיקה הצליחה
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # מחיקת הסשן
        cursor.execute('''
        DELETE FROM chat_sessions WHERE session_id = ?
        ''', (session_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            # שליחת אות
            self.session_deleted.emit(session_id)
            
            # איפוס הסשן הנוכחי אם זה הסשן שנמחק
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
        
        return success
    
    def add_message(self, text: str, sender: str) -> ChatMessage:
        """
        הוספת הודעה לסשן הנוכחי
        
        Args:
            text (str): תוכן ההודעה
            sender (str): שולח ההודעה ("user", "ai", או "system")
        
        Returns:
            ChatMessage: ההודעה שנוספה
        """
        # יצירת סשן חדש אם אין סשן נוכחי
        if self.current_session is None:
            self.create_session()
        
        # יצירת הודעה
        message = ChatMessage(text=text, sender=sender)
        
        # הוספת ההודעה לסשן
        self.current_session.add_message(message)
        
        # שמירת הסשן
        self._save_session(self.current_session)
        
        return message
    
    def clear_current_session(self) -> None:
        """ניקוי הסשן הנוכחי"""
        if self.current_session:
            self.current_session.messages = []
            self._save_session(self.current_session)
    
    def get_current_session(self) -> Optional[ChatSession]:
        """
        קבלת הסשן הנוכחי
        
        Returns:
            Optional[ChatSession]: הסשן הנוכחי, או None אם אין סשן נוכחי
        """
        return self.current_session