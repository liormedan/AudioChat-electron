import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple




class ChatMessage:
    """מודל להודעת צ'אט"""
    
    def __init__(self, text: str, sender: str, timestamp: Optional[datetime] = None, message_id: Optional[str] = None):
        """
        יוצר הודעת צ'אט חדשה
        
        Args:
            text (str): תוכן ההודעה
            sender (str): שולח ההודעה ("user", "ai", או "system")
            timestamp (datetime, optional): זמן שליחת ההודעה
            message_id (str, optional): מזהה ייחודי להודעה
        """
        self.text = text
        self.sender = sender
        self.timestamp = timestamp or datetime.now()
        self.message_id = message_id or f"{int(datetime.now().timestamp())}-{id(self)}"
        self.is_read = True
        self.reactions = []
        self.attachments = []
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת ההודעה למילון"""
        return {
            "text": self.text,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id,
            "is_read": self.is_read,
            "reactions": self.reactions,
            "attachments": self.attachments
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """יצירת הודעה ממילון"""
        message = cls(
            text=data["text"],
            sender=data["sender"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data.get("message_id")
        )
        
        # טעינת שדות נוספים אם קיימים
        if "is_read" in data:
            message.is_read = data["is_read"]
        if "reactions" in data:
            message.reactions = data["reactions"]
        if "attachments" in data:
            message.attachments = data["attachments"]
            
        return message
    
    def add_reaction(self, reaction: str) -> None:
        """
        הוספת תגובה להודעה
        
        Args:
            reaction (str): תגובה להוספה (אימוג'י)
        """
        if reaction not in self.reactions:
            self.reactions.append(reaction)
    
    def remove_reaction(self, reaction: str) -> None:
        """
        הסרת תגובה מההודעה
        
        Args:
            reaction (str): תגובה להסרה
        """
        if reaction in self.reactions:
            self.reactions.remove(reaction)
    
    def add_attachment(self, attachment: Dict[str, Any]) -> None:
        """
        הוספת קובץ מצורף להודעה
        
        Args:
            attachment (Dict[str, Any]): מידע על הקובץ המצורף
        """
        self.attachments.append(attachment)
    
    def mark_as_read(self) -> None:
        """סימון ההודעה כנקראה"""
        self.is_read = True
    
    def mark_as_unread(self) -> None:
        """סימון ההודעה כלא נקראה"""
        self.is_read = False


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
        self.pagination = {
            "page": 1,
            "page_size": 50,
            "total_messages": len(self.messages),
            "total_pages": 1
        }
    
    def add_message(self, message: ChatMessage) -> None:
        """הוספת הודעה לסשן"""
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # עדכון מידע על עימוד
        self.pagination["total_messages"] += 1
        self.pagination["total_pages"] = (self.pagination["total_messages"] + self.pagination["page_size"] - 1) // self.pagination["page_size"]
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת הסשן למילון"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "messages": [message.to_dict() for message in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "pagination": self.pagination
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
        
        # טעינת מידע על עימוד אם קיים
        if "pagination" in data:
            session.pagination = data["pagination"]
        
        return session


class ChatService:
    """שירות לניהול צ'אטים"""
    
    def __init__(self, db_path: str = None, llm_service=None):
        """
        יוצר שירות צ'אט חדש
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים
        """
        
        self.llm_service = llm_service
        
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
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            model_id TEXT NOT NULL,
            user_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            is_archived BOOLEAN DEFAULT FALSE,
            metadata TEXT DEFAULT '{}'
        )
        ''')

        # יצירת טבלת הודעות
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            model_id TEXT,
            tokens_used INTEGER,
            response_time REAL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
        ''')

        # אינדקסים לביצועים
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp)')

        conn.commit()
        conn.close()
    
    def create_session(self, title: str = "שיחה חדשה", model_id: str = "default", user_id: str = None) -> ChatSession:
        """
        יצירת סשן חדש
        
        Args:
            title (str, optional): כותרת הסשן
        
        Returns:
            ChatSession: הסשן החדש
        """
        # יצירת מזהה סשן
        session_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

        # יצירת סשן
        session = ChatSession(session_id=session_id, title=title)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            '''INSERT INTO chat_sessions (id, title, model_id, user_id, created_at, updated_at, message_count, metadata)
               VALUES (?, ?, ?, ?, ?, ?, 0, '{}')''',
            (session_id, title, model_id, user_id, now, now)
        )
        conn.commit()
        conn.close()
        
        # הגדרת הסשן הנוכחי
        self.current_session = session
        
        return session
    
    def _save_session(self, session: ChatSession) -> None:
        """עדכון נתוני הסשן במסד הנתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''UPDATE chat_sessions SET title = ?, updated_at = ?, message_count = ? WHERE id = ?''',
            (
                session.title,
                session.updated_at.isoformat(),
                len(session.messages),
                session.session_id,
            ),
        )

        conn.commit()
        conn.close()
        
        # שליחת אות
        
    
    def load_session(self, session_id: str, page: int = 1, page_size: int = 50) -> Optional[ChatSession]:
        """
        טעינת סשן ממסד הנתונים עם תמיכה בעימוד
        
        Args:
            session_id (str): מזהה הסשן
            page (int, optional): מספר העמוד לטעינה (ברירת מחדל: 1)
            page_size (int, optional): גודל העמוד (מספר הודעות מקסימלי, ברירת מחדל: 50)
        
        Returns:
            Optional[ChatSession]: הסשן שנטען, או None אם לא נמצא
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, created_at, updated_at FROM chat_sessions WHERE id = ?
        ''', (session_id,))
        session_row = cursor.fetchone()
        if not session_row:
            conn.close()
            return None

        offset = (page - 1) * page_size
        cursor.execute(
            '''SELECT id, role, content, timestamp FROM chat_messages
               WHERE session_id = ? ORDER BY timestamp LIMIT ? OFFSET ?''',
            (session_id, page_size, offset)
        )
        message_rows = cursor.fetchall()

        cursor.execute('SELECT COUNT(*) FROM chat_messages WHERE session_id = ?', (session_id,))
        total_messages = cursor.fetchone()[0]
        conn.close()

        messages = [
            ChatMessage(
                text=row[2],
                sender=row[1],
                timestamp=datetime.fromisoformat(row[3]),
                message_id=row[0],
            )
            for row in message_rows
        ]

        session = ChatSession(session_id=session_row[0], title=session_row[1], messages=messages)
        session.created_at = datetime.fromisoformat(session_row[2])
        session.updated_at = datetime.fromisoformat(session_row[3])
        session.pagination = {
            "page": page,
            "page_size": page_size,
            "total_messages": total_messages,
            "total_pages": (total_messages + page_size - 1) // page_size,
        }
        
        # הגדרת הסשן הנוכחי
        self.current_session = session
        
        # שליחת אות
        
        
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
        SELECT id, title, updated_at FROM chat_sessions
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
        cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            
            
            # איפוס הסשן הנוכחי אם זה הסשן שנמחק
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
        
        return success
    
    def add_message(self, text: str, sender: str, file_info=None) -> ChatMessage:
        """
        הוספת הודעה לסשן הנוכחי
        
        Args:
            text (str): תוכן ההודעה
            sender (str): שולח ההודעה ("user", "ai", או "system")
            file_info (FileInfo, optional): מידע על קובץ מצורף
        
        Returns:
            ChatMessage: ההודעה שנוספה
        """
        # יצירת סשן חדש אם אין סשן נוכחי
        if self.current_session is None:
            self.create_session()
        
        # יצירת הודעה
        message = ChatMessage(text=text, sender=sender)
        
        # הוספת קובץ מצורף אם יש
        if file_info:
            attachment = {
                "type": "audio_file",
                "name": file_info.name,
                "path": file_info.path,
                "size": file_info.size,
                "format": file_info.format,
                "duration": file_info.duration,
                "upload_date": file_info.upload_date.isoformat() if hasattr(file_info.upload_date, 'isoformat') else str(file_info.upload_date)
            }
            message.add_attachment(attachment)
        
        # הוספת ההודעה למסד הנתונים
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO chat_messages (id, session_id, role, content, timestamp)
               VALUES (?, ?, ?, ?, ?)''',
            (
                message.message_id,
                self.current_session.session_id,
                sender,
                text,
                message.timestamp.isoformat(),
            ),
        )
        cursor.execute(
            'UPDATE chat_sessions SET updated_at = ?, message_count = message_count + 1 WHERE id = ?',
            (message.timestamp.isoformat(), self.current_session.session_id),
        )
        conn.commit()
        conn.close()

        # הוספת ההודעה לאובייקט הסשן בזיכרון
        self.current_session.add_message(message)
        
        return message
    
    def clear_current_session(self) -> None:
        """ניקוי הסשן הנוכחי"""
        if self.current_session:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (self.current_session.session_id,))
            cursor.execute('UPDATE chat_sessions SET message_count = 0 WHERE id = ?', (self.current_session.session_id,))
            conn.commit()
            conn.close()

            self.current_session.messages = []
            self._save_session(self.current_session)
    
    def get_current_session(self) -> Optional[ChatSession]:
        """
        קבלת הסשן הנוכחי
        
        Returns:
            Optional[ChatSession]: הסשן הנוכחי, או None אם אין סשן נוכחי
        """
        return self.current_session
        
    def get_session_message_count(self, session_id: str) -> int:
        """
        קבלת מספר ההודעות בסשן
        
        Args:
            session_id (str): מזהה הסשן
        
        Returns:
            int: מספר ההודעות בסשן, או 0 אם הסשן לא נמצא
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT message_count FROM chat_sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        if row:
            count = row[0]
        else:
            count = 0

        conn.close()
        return count

    def generate_ai_reply(self, text: str) -> Optional[str]:
        """Generate an AI response using the connected LLM service"""
        if not self.llm_service:
            return None

        try:
            messages = [{"role": "user", "content": text}]
            response = self.llm_service.generate_chat_response(messages)
            if response and getattr(response, "success", False):
                self.add_message(response.content, "ai")
                return response.content
        except Exception as e:
            print(f"AI generation error: {e}")

        return None

    def suggest_models_for_prompt(self, prompt: str) -> List[str]:
        """Return model name suggestions based on the prompt"""
        if not self.llm_service:
            return []

        lower = prompt.lower()
        if any(k in lower for k in ["code", "תכנת"]):
            task = "code"
        elif any(k in lower for k in ["summary", "summarize", "סיכום"]):
            task = "summarize"
        elif any(k in lower for k in ["transcribe", "תמלל", "תמלול"]):
            task = "transcribe"
        elif any(k in lower for k in ["analyze", "analysis", "ניתוח"]):
            task = "analyze"
        else:
            task = "chat"

        models = self.llm_service.suggest_models_for_task(task)
        return [m.name for m in models]
