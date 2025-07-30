import json
import os
import sqlite3
import logging
import uuid
from datetime import datetime
from typing import Optional, List

from backend.models import ChatSession, SessionNotFoundError

logger = logging.getLogger(__name__)


class SessionService:
    """Manage chat sessions"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            app_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "chat_history.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
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
            """
        )
        conn.commit()
        conn.close()

    def create_session(self, title: str = None, model_id: str = None, user_id: str = None) -> ChatSession:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        session = ChatSession(
            id=session_id,
            title=title or "New Chat",
            model_id=model_id or "default",
            user_id=user_id,
            created_at=now,
            updated_at=now,
            message_count=0,
        )
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_sessions VALUES (?,?,?,?,?,?,?,?,?)",
            (
                session.id,
                session.title,
                session.model_id,
                session.user_id,
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
                session.message_count,
                int(session.is_archived),
                json.dumps(session.metadata),
            ),
        )
        conn.commit()
        conn.close()
        logger.info(f"Created session {session.id}")
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return ChatSession.from_row(row)

    def list_user_sessions(self, user_id: str = None, limit: int = 50) -> List[ChatSession]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if user_id:
            cursor.execute(
                "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?",
                (user_id, limit),
            )
        else:
            cursor.execute(
                "SELECT * FROM chat_sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
        rows = cursor.fetchall()
        conn.close()
        return [ChatSession.from_row(r) for r in rows]

    def update_session(self, session_id: str, **updates) -> bool:
        if not updates:
            return False
        fields = []
        values = []
        for key, value in updates.items():
            if key == "metadata":
                value = json.dumps(value)
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(session_id)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE chat_sessions SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
            (*values[:-1], datetime.utcnow().isoformat(), values[-1]),
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def delete_session(self, session_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def increment_message_count(self, session_id: str, count: int = 1) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chat_sessions SET message_count = message_count + ?, updated_at = ? WHERE id = ?",
            (count, datetime.utcnow().isoformat(), session_id),
        )
        conn.commit()
        conn.close()
