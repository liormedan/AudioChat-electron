import json
import os
import sqlite3
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from backend.models.chat import Message

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """Store and retrieve chat messages"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            app_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "llm_data.db")  # Use same DB as LLM service
        self.db_path = db_path
        # No need to init DB here - it's handled by LLM service

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
        """Export session messages in specified format"""
        messages = self.get_session_messages(session_id)
        
        if format == "json":
            data = [m.to_dict() for m in messages]
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format == "markdown":
            return self._export_as_markdown(messages)
        elif format == "txt":
            return self._export_as_text(messages)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_as_markdown(self, messages: List[Message]) -> str:
        """Export messages as markdown format"""
        lines = ["# Chat Session Export\n"]
        
        for message in messages:
            timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            role_emoji = "👤" if message.role == "user" else "🤖" if message.role == "assistant" else "⚙️"
            
            lines.append(f"## {role_emoji} {message.role.title()} - {timestamp}\n")
            lines.append(f"{message.content}\n")
            
            if message.model_id:
                lines.append(f"*Model: {message.model_id}*")
            if message.tokens_used:
                lines.append(f"*Tokens: {message.tokens_used}*")
            if message.response_time:
                lines.append(f"*Response time: {message.response_time:.2f}s*")
            
            lines.append("\n---\n")
        
        return "\n".join(lines)

    def _export_as_text(self, messages: List[Message]) -> str:
        """Export messages as plain text format"""
        lines = ["Chat Session Export", "=" * 50, ""]
        
        for message in messages:
            timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"[{timestamp}] {message.role.upper()}: {message.content}")
            lines.append("")
        
        return "\n".join(lines)

    def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (session_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def delete_message(self, message_id: str) -> bool:
        """Delete a specific message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE id = ?", (message_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        logger.info(f"Deleted message {message_id}")
        return success

    def delete_session_messages(self, session_id: str) -> int:
        """Delete all messages for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info(f"Deleted {count} messages from session {session_id}")
        return count

    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """Get a specific message by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Message.from_row(row)
        return None

    def update_message(self, message_id: str, **updates) -> bool:
        """Update a message"""
        if not updates:
            return False
        
        fields = []
        values = []
        for key, value in updates.items():
            if key == "metadata":
                value = json.dumps(value)
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(message_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE chat_messages SET {', '.join(fields)} WHERE id = ?",
            values
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_session_statistics(self, session_id: str) -> dict:
        """Get detailed statistics for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute(
            "SELECT role, COUNT(*) FROM chat_messages WHERE session_id = ? GROUP BY role",
            (session_id,)
        )
        role_counts = dict(cursor.fetchall())
        
        # Token usage
        cursor.execute(
            "SELECT SUM(tokens_used), AVG(tokens_used), MAX(tokens_used) FROM chat_messages WHERE session_id = ? AND tokens_used IS NOT NULL",
            (session_id,)
        )
        token_stats = cursor.fetchone()
        
        # Response times
        cursor.execute(
            "SELECT AVG(response_time), MIN(response_time), MAX(response_time) FROM chat_messages WHERE session_id = ? AND response_time IS NOT NULL",
            (session_id,)
        )
        time_stats = cursor.fetchone()
        
        # Date range
        cursor.execute(
            "SELECT MIN(timestamp), MAX(timestamp) FROM chat_messages WHERE session_id = ?",
            (session_id,)
        )
        date_range = cursor.fetchone()
        
        conn.close()
        
        return {
            "session_id": session_id,
            "message_counts": {
                "total": sum(role_counts.values()),
                "user": role_counts.get("user", 0),
                "assistant": role_counts.get("assistant", 0),
                "system": role_counts.get("system", 0)
            },
            "token_usage": {
                "total": token_stats[0] if token_stats[0] else 0,
                "average": token_stats[1] if token_stats[1] else 0,
                "maximum": token_stats[2] if token_stats[2] else 0
            },
            "response_times": {
                "average": time_stats[0] if time_stats[0] else 0,
                "minimum": time_stats[1] if time_stats[1] else 0,
                "maximum": time_stats[2] if time_stats[2] else 0
            },
            "date_range": {
                "first_message": date_range[0],
                "last_message": date_range[1]
            }
        }
