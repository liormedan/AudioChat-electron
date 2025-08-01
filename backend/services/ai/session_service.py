import json
import os
import sqlite3
import logging
import uuid
from datetime import datetime
from typing import Optional, List

from backend.models.chat import ChatSession, SessionNotFoundError
from backend.services.security.audit_service import log_user_action, AuditSeverity

logger = logging.getLogger(__name__)


class SessionService:
    """Manage chat sessions"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            app_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "llm_data.db")  # Use same DB as LLM service
        self.db_path = db_path
        # No need to init DB here - it's handled by LLM service



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
        
        # Log audit event
        try:
            log_user_action(
                action="session_created",
                user_id=user_id,
                session_id=session.id,
                details={
                    "title": session.title,
                    "model_id": session.model_id
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log audit event for session creation: {e}")
        
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
        
        # Log audit event
        if success:
            try:
                log_user_action(
                    action="session_deleted",
                    session_id=session_id,
                    details={"permanent_deletion": True}
                )
            except Exception as e:
                logger.warning(f"Failed to log audit event for session deletion: {e}")
        
        return success

    def increment_message_count(self, session_id: str, count: int = 1) -> None:
        """Increment message count for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chat_sessions SET message_count = message_count + ?, updated_at = ? WHERE id = ?",
            (count, datetime.utcnow().isoformat(), session_id),
        )
        conn.commit()
        conn.close()

    def archive_session(self, session_id: str) -> bool:
        """Archive a session"""
        return self.update_session(session_id, is_archived=True)

    def unarchive_session(self, session_id: str) -> bool:
        """Unarchive a session"""
        return self.update_session(session_id, is_archived=False)

    def get_session_stats(self, session_id: str) -> Optional[dict]:
        """Get session statistics"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get message statistics
        cursor.execute(
            "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM chat_messages WHERE session_id = ?",
            (session_id,)
        )
        msg_stats = cursor.fetchone()
        
        # Get token usage
        cursor.execute(
            "SELECT SUM(tokens_used), AVG(response_time) FROM chat_messages WHERE session_id = ? AND tokens_used IS NOT NULL",
            (session_id,)
        )
        token_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "session_id": session_id,
            "title": session.title,
            "model_id": session.model_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": msg_stats[0] if msg_stats[0] else 0,
            "first_message": msg_stats[1],
            "last_message": msg_stats[2],
            "total_tokens": token_stats[0] if token_stats[0] else 0,
            "avg_response_time": token_stats[1] if token_stats[1] else 0,
            "is_archived": session.is_archived
        }

    def search_sessions(self, query: str, user_id: str = None, limit: int = 50) -> List[ChatSession]:
        """Search sessions by title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute(
                "SELECT * FROM chat_sessions WHERE title LIKE ? AND user_id = ? ORDER BY updated_at DESC LIMIT ?",
                (f"%{query}%", user_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM chat_sessions WHERE title LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (f"%{query}%", limit)
            )
        
        rows = cursor.fetchall()
        conn.close()
        return [ChatSession.from_row(r) for r in rows]

    def get_recent_sessions(self, user_id: str = None, limit: int = 10) -> List[ChatSession]:
        """Get most recently updated sessions"""
        return self.list_user_sessions(user_id=user_id, limit=limit)

    def cleanup_old_sessions(self, days_old: int = 30, dry_run: bool = True) -> int:
        """Clean up old archived sessions"""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find sessions to delete
        cursor.execute(
            "SELECT id FROM chat_sessions WHERE is_archived = 1 AND updated_at < ?",
            (cutoff_date,)
        )
        sessions_to_delete = cursor.fetchall()
        
        if not dry_run and sessions_to_delete:
            # Delete the sessions
            session_ids = [s[0] for s in sessions_to_delete]
            placeholders = ','.join(['?' for _ in session_ids])
            cursor.execute(f"DELETE FROM chat_sessions WHERE id IN ({placeholders})", session_ids)
            conn.commit()
            logger.info(f"Deleted {len(sessions_to_delete)} old sessions")
        
        conn.close()
        return len(sessions_to_delete)
