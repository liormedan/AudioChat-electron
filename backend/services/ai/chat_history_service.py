import json
import os
import sqlite3
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from backend.models import Message

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """Store and retrieve chat messages"""

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
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                model_id TEXT,
                tokens_used INTEGER,
                response_time REAL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
        conn.close()

    def save_message(self, session_id: str, message: Message) -> str:
        if not message.id:
            message.id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_messages VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                message.id,
                session_id,
                message.role,
                message.content,
                message.timestamp.isoformat(),
                message.model_id,
                message.tokens_used,
                message.response_time,
                json.dumps(message.metadata),
            ),
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved message {message.id} to session {session_id}")
        return message.id

    def get_session_messages(self, session_id: str, limit: int = None, offset: int = 0) -> List[Message]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC"
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            cursor.execute(query, (session_id, limit, offset))
        else:
            cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Message.from_row(r) for r in rows]

    def search_messages(self, query: str, user_id: str = None, session_id: str = None) -> List[Message]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        sql = "SELECT m.* FROM chat_messages m JOIN chat_sessions s ON m.session_id = s.id WHERE m.content LIKE ?"
        params = [f"%{query}%"]
        if user_id:
            sql += " AND s.user_id = ?"
            params.append(user_id)
        if session_id:
            sql += " AND m.session_id = ?"
            params.append(session_id)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [Message.from_row(r) for r in rows]

    def export_session(self, session_id: str, format: str = "json") -> str:
        messages = self.get_session_messages(session_id)
        data = [m.to_dict() for m in messages]
        if format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        raise ValueError("Unsupported export format")
