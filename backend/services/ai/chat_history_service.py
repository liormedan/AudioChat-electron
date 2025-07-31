import json
import os
import sqlite3
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from backend.models.chat import Message
from backend.services.security.encryption_service import encryption_service

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
        
        # Encrypt message content before saving
        try:
            encrypted_content = encryption_service.encrypt_message(message.content, message.id)
            logger.debug(f"Encrypted message {message.id}")
        except Exception as e:
            logger.warning(f"Failed to encrypt message {message.id}: {e}. Saving unencrypted.")
            encrypted_content = message.content
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_messages VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                message.id,
                session_id,
                message.role.value if hasattr(message.role, "value") else message.role,
                encrypted_content,  # Store encrypted content
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

    def get_session_messages(self, session_id: str, limit: int = None, offset: int = 0, as_str: bool = True) -> List[Message]:
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
        
        messages = []
        for row in rows:
            message = Message.from_row(row)
            
            # Decrypt message content
            try:
                decrypted_content = encryption_service.decrypt_message(message.content, message.id)
                message.content = decrypted_content
                logger.debug(f"Decrypted message {message.id}")
            except Exception as e:
                logger.warning(f"Failed to decrypt message {message.id}: {e}. Using content as-is.")
                # Content remains as stored (might be unencrypted)
            
            messages.append(message)
        
        if as_str:
            for m in messages:
                if hasattr(m.role, "value"):
                    m.role = m.role.value
                if hasattr(m.type, "value"):
                    m.type = m.type.value
        return messages

    def search_messages(self, query: str, user_id: str = None, session_id: str = None) -> List[Message]:
        """
        Search messages by content. Note: This searches encrypted content,
        so results may be limited when encryption is enabled.
        For better search functionality, consider implementing a search index.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all messages first, then decrypt and search
        # This is less efficient but necessary for encrypted content
        sql = "SELECT m.* FROM chat_messages m JOIN chat_sessions s ON m.session_id = s.id"
        params = []
        
        conditions = []
        if user_id:
            conditions.append("s.user_id = ?")
            params.append(user_id)
        if session_id:
            conditions.append("m.session_id = ?")
            params.append(session_id)
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Decrypt and search
        matching_messages = []
        for row in rows:
            message = Message.from_row(row)
            
            # Decrypt message content for search
            try:
                decrypted_content = encryption_service.decrypt_message(message.content, message.id)
                message.content = decrypted_content
                
                # Check if query matches decrypted content
                if query.lower() in decrypted_content.lower():
                    matching_messages.append(message)
                    
            except Exception as e:
                logger.warning(f"Failed to decrypt message {message.id} for search: {e}")
                # Try searching in original content (might be unencrypted)
                if query.lower() in message.content.lower():
                    matching_messages.append(message)
        
        return matching_messages

    def export_session(self, session_id: str, format: str = "json") -> str:
        """Export session messages in specified format"""
        messages = self.get_session_messages(session_id, as_str=False)
        
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
            role = message.role.value if hasattr(message.role, "value") else message.role
            role_emoji = "👤" if role == "user" else "🤖" if role == "assistant" else "⚙️"

            lines.append(f"## {role_emoji} {role.title()} - {timestamp}\n")
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
            role = message.role.value if hasattr(message.role, "value") else message.role
            lines.append(f"[{timestamp}] {role.upper()}: {message.content}")
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

    def get_message_by_id(self, message_id: str, as_str: bool = True) -> Optional[Message]:
        """Get a specific message by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            msg = Message.from_row(row)
            
            # Decrypt message content
            try:
                decrypted_content = encryption_service.decrypt_message(msg.content, msg.id)
                msg.content = decrypted_content
                logger.debug(f"Decrypted message {msg.id}")
            except Exception as e:
                logger.warning(f"Failed to decrypt message {msg.id}: {e}. Using content as-is.")
                # Content remains as stored (might be unencrypted)
            
            if as_str:
                if hasattr(msg.role, "value"):
                    msg.role = msg.role.value
                if hasattr(msg.type, "value"):
                    msg.type = msg.type.value
            return msg
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

    def get_encryption_status(self) -> dict:
        """Get encryption status and statistics"""
        try:
            from backend.services.security.encryption_service import get_encryption_status
            return get_encryption_status()
        except Exception as e:
            logger.error(f"Failed to get encryption status: {e}")
            return {
                "encryption_enabled": False,
                "error": str(e)
            }

    def migrate_to_encryption(self) -> dict:
        """
        Migrate existing unencrypted messages to encrypted format.
        This should be run once when enabling encryption on existing data.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all messages
        cursor.execute("SELECT id, content FROM chat_messages")
        messages = cursor.fetchall()
        
        migrated_count = 0
        failed_count = 0
        
        for message_id, content in messages:
            try:
                # Try to decrypt first - if it works, it's already encrypted
                try:
                    encryption_service.decrypt_message(content, message_id)
                    continue  # Already encrypted, skip
                except:
                    pass  # Not encrypted, proceed with encryption
                
                # Encrypt the content
                encrypted_content = encryption_service.encrypt_message(content, message_id)
                
                # Update the message
                cursor.execute(
                    "UPDATE chat_messages SET content = ? WHERE id = ?",
                    (encrypted_content, message_id)
                )
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate message {message_id}: {e}")
                failed_count += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"Migration completed: {migrated_count} messages encrypted, {failed_count} failed")
        
        return {
            "migrated_count": migrated_count,
            "failed_count": failed_count,
            "total_messages": len(messages)
        }

    def verify_message_encryption(self, session_id: str = None) -> dict:
        """
        Verify that messages can be properly decrypted.
        Useful for checking encryption integrity.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute("SELECT id, content FROM chat_messages WHERE session_id = ?", (session_id,))
        else:
            cursor.execute("SELECT id, content FROM chat_messages")
        
        messages = cursor.fetchall()
        conn.close()
        
        verified_count = 0
        failed_count = 0
        failed_messages = []
        
        for message_id, content in messages:
            try:
                # Try to decrypt
                decrypted = encryption_service.decrypt_message(content, message_id)
                if decrypted:  # Successfully decrypted
                    verified_count += 1
                else:
                    failed_count += 1
                    failed_messages.append(message_id)
            except Exception as e:
                failed_count += 1
                failed_messages.append(message_id)
                logger.warning(f"Failed to verify message {message_id}: {e}")
        
        return {
            "total_messages": len(messages),
            "verified_count": verified_count,
            "failed_count": failed_count,
            "failed_messages": failed_messages[:10],  # Limit to first 10 for brevity
            "integrity_ok": failed_count == 0
        }
