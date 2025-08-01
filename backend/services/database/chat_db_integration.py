"""
Chat Database Integration Service
שירות אינטגרציה בין מערכת השיחות למסד הנתונים המותאם
"""

import logging
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import asdict

from backend.services.database.optimized_db_service import (
    optimized_db, BatchOperation, QueryType
)
from backend.services.cache.chat_cache_service import chat_cache
from backend.services.security.encryption_service import encryption_service
from backend.services.security.audit_service import log_user_action, AuditSeverity
from backend.models.chat import ChatSession, Message

logger = logging.getLogger(__name__)


class OptimizedChatHistoryService:
    """
    שירות היסטוריית שיחות מותאם לביצועים
    משתמש במסד הנתונים המותאם ו-cache
    """
    
    def __init__(self):
        self.db = optimized_db
        self.cache = chat_cache
    
    def save_message(self, session_id: str, message: Message) -> str:
        """שמירת הודעה בודדת עם אופטימיזציות"""
        if not message.id:
            message.id = str(uuid.uuid4())
        
        # הצפנת תוכן ההודעה
        encrypted_content = message.content
        is_encrypted = False
        
        try:
            encrypted_content = encryption_service.encrypt_message(message.content, message.id)
            is_encrypted = True
            logger.debug(f"Encrypted message {message.id}")
        except Exception as e:
            logger.warning(f"Failed to encrypt message {message.id}: {e}. Saving unencrypted.")
        
        # הכנת נתונים לשמירה
        message_data = {
            'id': message.id,
            'session_id': session_id,
            'role': message.role.value if hasattr(message.role, "value") else message.role,
            'content': encrypted_content,
            'timestamp': message.timestamp.isoformat() if message.timestamp else datetime.utcnow().isoformat(),
            'model_id': message.model_id,
            'tokens_used': message.tokens_used,
            'response_time': message.response_time,
            'metadata': message.metadata or {},
            'is_encrypted': is_encrypted
        }
        
        # שמירה במסד הנתונים
        try:
            self.db.save_messages_batch([message_data])
            
            # עדכון מספר הודעות ב-session
            self._update_session_message_count(session_id, 1)
            
            # ביטול cache של הודעות session
            self.cache.invalidate_session_messages(session_id)
            
            logger.info(f"Saved message {message.id} to session {session_id}")
            
            # רישום אירוע audit
            log_user_action(
                action="message_saved",
                session_id=session_id,
                details={
                    "message_id": message.id,
                    "role": message_data['role'],
                    "encrypted": is_encrypted,
                    "content_length": len(message.content)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to save message {message.id}: {e}")
            raise
        
        return message.id
    
    def save_messages_batch(self, session_id: str, messages: List[Message]) -> List[str]:
        """שמירת הודעות מרובות ב-batch"""
        if not messages:
            return []
        
        messages_data = []
        message_ids = []
        
        for message in messages:
            if not message.id:
                message.id = str(uuid.uuid4())
            
            message_ids.append(message.id)
            
            # הצפנת תוכן
            encrypted_content = message.content
            is_encrypted = False
            
            try:
                encrypted_content = encryption_service.encrypt_message(message.content, message.id)
                is_encrypted = True
            except Exception as e:
                logger.warning(f"Failed to encrypt message {message.id}: {e}")
            
            message_data = {
                'id': message.id,
                'session_id': session_id,
                'role': message.role.value if hasattr(message.role, "value") else message.role,
                'content': encrypted_content,
                'timestamp': message.timestamp.isoformat() if message.timestamp else datetime.utcnow().isoformat(),
                'model_id': message.model_id,
                'tokens_used': message.tokens_used,
                'response_time': message.response_time,
                'metadata': message.metadata or {},
                'is_encrypted': is_encrypted
            }
            
            messages_data.append(message_data)
        
        try:
            # שמירה ב-batch
            affected_rows = self.db.save_messages_batch(messages_data)
            
            # עדכון מספר הודעות
            self._update_session_message_count(session_id, len(messages))
            
            # ביטול cache
            self.cache.invalidate_session_messages(session_id)
            
            logger.info(f"Saved {affected_rows} messages to session {session_id}")
            
            # רישום אירוע audit
            log_user_action(
                action="messages_batch_saved",
                session_id=session_id,
                details={
                    "message_count": len(messages),
                    "affected_rows": affected_rows
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to save messages batch: {e}")
            raise
        
        return message_ids
    
    def get_session_messages(self, session_id: str, limit: int = 50, offset: int = 0, 
                           order: str = 'ASC', use_cache: bool = True) -> List[Message]:
        """קבלת הודעות session עם אופטימיזציות"""
        
        # ניסיון קבלה מ-cache (רק לעמוד הראשון)
        if use_cache and offset == 0 and order.upper() == 'ASC':
            cached_messages = self.cache.get_session_messages(session_id, limit)
            if cached_messages:
                try:
                    messages = []
                    for msg_data in cached_messages:
                        message = Message.from_dict(msg_data)
                        
                        # פענוח הודעה
                        if msg_data.get('is_encrypted', False):
                            try:
                                decrypted_content = encryption_service.decrypt_message(
                                    message.content, message.id
                                )
                                message.content = decrypted_content
                            except Exception as e:
                                logger.warning(f"Failed to decrypt cached message {message.id}: {e}")
                        
                        messages.append(message)
                    
                    return messages[:limit]
                    
                except Exception as e:
                    logger.warning(f"Failed to process cached messages: {e}")
        
        # קבלה ממסד הנתונים
        try:
            result = self.db.get_session_messages_paginated(
                session_id=session_id,
                limit=limit,
                offset=offset,
                order=order
            )
            
            messages = []
            for msg_data in result['messages']:
                message = Message(
                    id=msg_data['id'],
                    role=msg_data['role'],
                    content=msg_data['content'],
                    timestamp=datetime.fromisoformat(msg_data['timestamp']),
                    model_id=msg_data['model_id'],
                    tokens_used=msg_data['tokens_used'],
                    response_time=msg_data['response_time'],
                    metadata=json.loads(msg_data['metadata']) if msg_data['metadata'] else {}
                )
                
                # פענוח הודעה
                if msg_data.get('is_encrypted', False):
                    try:
                        decrypted_content = encryption_service.decrypt_message(
                            message.content, message.id
                        )
                        message.content = decrypted_content
                    except Exception as e:
                        logger.warning(f"Failed to decrypt message {message.id}: {e}")
                
                messages.append(message)
            
            # שמירה ב-cache (רק לעמוד הראשון)
            if use_cache and offset == 0 and order.upper() == 'ASC' and messages:
                try:
                    cached_data = [msg.to_dict() for msg in messages]
                    self.cache.set_session_messages(session_id, cached_data, limit)
                except Exception as e:
                    logger.warning(f"Failed to cache messages: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get session messages: {e}")
            raise
    
    def search_messages(self, query: str, user_id: str = None, session_id: str = None, 
                       limit: int = 100, use_cache: bool = True) -> List[Message]:
        """חיפוש הודעות מותאם"""
        
        # ניסיון קבלה מ-cache
        cache_key = None
        if use_cache:
            filters = {"user_id": user_id, "session_id": session_id, "limit": limit}
            cached_results = self.cache.get_search_results(query, filters)
            if cached_results:
                try:
                    return [Message.from_dict(msg_data) for msg_data in cached_results]
                except Exception as e:
                    logger.warning(f"Failed to process cached search results: {e}")
        
        # חיפוש במסד הנתונים
        try:
            results = self.db.search_messages_optimized(
                query=query,
                user_id=user_id,
                session_id=session_id,
                limit=limit
            )
            
            messages = []
            for msg_data in results:
                message = Message(
                    id=msg_data['id'],
                    role=msg_data['role'],
                    content=msg_data['content'],
                    timestamp=datetime.fromisoformat(msg_data['timestamp']),
                    model_id=msg_data['model_id'],
                    tokens_used=msg_data['tokens_used'],
                    response_time=msg_data['response_time'],
                    metadata={}
                )
                
                # פענוח הודעה (הנחה שהחיפוש מחזיר תוכן מפוענח)
                # בפועל, צריך לשפר את החיפוש לעבוד עם הצפנה
                
                messages.append(message)
            
            # שמירה ב-cache
            if use_cache and messages:
                try:
                    filters = {"user_id": user_id, "session_id": session_id, "limit": limit}
                    cached_data = [msg.to_dict() for msg in messages]
                    self.cache.set_search_results(query, filters, cached_data)
                except Exception as e:
                    logger.warning(f"Failed to cache search results: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            raise
    
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """קבלת הודעה לפי ID"""
        try:
            cursor = self.db.execute_query(
                "SELECT * FROM chat_messages WHERE id = ?",
                (message_id,),
                QueryType.SELECT
            )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            msg_data = dict(row)
            message = Message(
                id=msg_data['id'],
                role=msg_data['role'],
                content=msg_data['content'],
                timestamp=datetime.fromisoformat(msg_data['timestamp']),
                model_id=msg_data['model_id'],
                tokens_used=msg_data['tokens_used'],
                response_time=msg_data['response_time'],
                metadata=json.loads(msg_data['metadata']) if msg_data['metadata'] else {}
            )
            
            # פענוח הודעה
            if msg_data.get('is_encrypted', False):
                try:
                    decrypted_content = encryption_service.decrypt_message(
                        message.content, message.id
                    )
                    message.content = decrypted_content
                except Exception as e:
                    logger.warning(f"Failed to decrypt message {message.id}: {e}")
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to get message {message_id}: {e}")
            return None
    
    def delete_message(self, message_id: str) -> bool:
        """מחיקת הודעה"""
        try:
            cursor = self.db.execute_query(
                "DELETE FROM chat_messages WHERE id = ?",
                (message_id,),
                QueryType.DELETE
            )
            
            success = cursor.rowcount > 0
            
            if success:
                # ביטול cache רלוונטי
                # כאן נצטרך לדעת את session_id כדי לבטל cache
                logger.info(f"Deleted message {message_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            return False
    
    def delete_session_messages(self, session_id: str) -> int:
        """מחיקת כל הודעות session"""
        try:
            cursor = self.db.execute_query(
                "DELETE FROM chat_messages WHERE session_id = ?",
                (session_id,),
                QueryType.DELETE
            )
            
            deleted_count = cursor.rowcount
            
            if deleted_count > 0:
                # עדכון מספר הודעות ב-session
                self._update_session_message_count(session_id, -deleted_count)
                
                # ביטול cache
                self.cache.invalidate_session_messages(session_id)
                
                logger.info(f"Deleted {deleted_count} messages from session {session_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete session messages: {e}")
            return 0
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """קבלת סטטיסטיקות session מותאמות"""
        try:
            # שימוש ב-query מותאם מהשירות המותאם
            session_data = self.db.get_session_with_stats(session_id)
            
            if not session_data:
                return {}
            
            # חישוב סטטיסטיקות נוספות
            cursor = self.db.execute_query(
                """SELECT 
                   role, 
                   COUNT(*) as count,
                   AVG(tokens_used) as avg_tokens,
                   AVG(response_time) as avg_response_time
                   FROM chat_messages 
                   WHERE session_id = ? AND tokens_used IS NOT NULL
                   GROUP BY role""",
                (session_id,),
                QueryType.SELECT
            )
            
            role_stats = {}
            for row in cursor.fetchall():
                role_data = dict(row)
                role_stats[role_data['role']] = {
                    'count': role_data['count'],
                    'avg_tokens': role_data['avg_tokens'] or 0,
                    'avg_response_time': role_data['avg_response_time'] or 0
                }
            
            return {
                "session_id": session_id,
                "title": session_data.get('title'),
                "message_count": session_data.get('actual_message_count', 0),
                "total_tokens": session_data.get('total_tokens_used', 0),
                "avg_response_time": session_data.get('avg_response_time', 0),
                "last_message_at": session_data.get('last_message_timestamp'),
                "role_statistics": role_stats,
                "created_at": session_data.get('created_at'),
                "updated_at": session_data.get('updated_at')
            }
            
        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {}
    
    def _update_session_message_count(self, session_id: str, count_delta: int):
        """עדכון מספר הודעות ב-session"""
        try:
            self.db.execute_query(
                """UPDATE chat_sessions 
                   SET message_count = message_count + ?, 
                       updated_at = ?,
                       last_message_at = ?
                   WHERE id = ?""",
                (count_delta, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), session_id),
                QueryType.UPDATE
            )
            
            # ביטול cache של session
            self.cache.invalidate_session(session_id)
            
        except Exception as e:
            logger.warning(f"Failed to update session message count: {e}")


class OptimizedSessionService:
    """
    שירות sessions מותאם לביצועים
    """
    
    def __init__(self):
        self.db = optimized_db
        self.cache = chat_cache
    
    def create_session(self, title: str = None, model_id: str = None, user_id: str = None) -> ChatSession:
        """יצירת session חדש"""
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
        
        try:
            # שמירה במסד הנתונים
            self.db.execute_query(
                """INSERT INTO chat_sessions 
                   (id, title, model_id, user_id, created_at, updated_at, message_count, is_archived, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                QueryType.INSERT
            )
            
            # שמירה ב-cache
            self.cache.set_session(session.id, session.to_dict())
            
            # ביטול cache של user sessions
            if user_id:
                self.cache.invalidate_user_sessions(user_id)
            
            logger.info(f"Created session {session.id}")
            
            # רישום אירוע audit
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
            logger.error(f"Failed to create session: {e}")
            raise
        
        return session
    
    def get_session(self, session_id: str, use_cache: bool = True) -> Optional[ChatSession]:
        """קבלת session"""
        
        # ניסיון קבלה מ-cache
        if use_cache:
            cached_session = self.cache.get_session(session_id)
            if cached_session:
                try:
                    return ChatSession.from_dict(cached_session)
                except Exception as e:
                    logger.warning(f"Failed to deserialize cached session: {e}")
        
        # קבלה ממסד הנתונים עם סטטיסטיקות
        try:
            session_data = self.db.get_session_with_stats(session_id)
            
            if not session_data:
                return None
            
            session = ChatSession(
                id=session_data['id'],
                title=session_data['title'],
                model_id=session_data['model_id'],
                user_id=session_data['user_id'],
                created_at=datetime.fromisoformat(session_data['created_at']),
                updated_at=datetime.fromisoformat(session_data['updated_at']),
                message_count=session_data.get('actual_message_count', 0),
                is_archived=bool(session_data['is_archived']),
                metadata=json.loads(session_data['metadata']) if session_data['metadata'] else {}
            )
            
            # שמירה ב-cache
            if use_cache:
                self.cache.set_session(session_id, session.to_dict())
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def list_user_sessions(self, user_id: str = None, limit: int = 50, offset: int = 0,
                          include_archived: bool = False, use_cache: bool = True) -> Dict[str, Any]:
        """קבלת sessions של משתמש עם pagination"""
        
        # ניסיון קבלה מ-cache (רק לעמוד הראשון)
        if use_cache and offset == 0 and user_id:
            cached_sessions = self.cache.get_user_sessions(user_id, limit)
            if cached_sessions:
                try:
                    sessions = [ChatSession.from_dict(session_data) for session_data in cached_sessions]
                    return {
                        "sessions": sessions,
                        "total_count": len(sessions),  # לא מדויק, אבל מהיר
                        "limit": limit,
                        "offset": offset,
                        "has_more": len(sessions) == limit,  # הערכה
                        "from_cache": True
                    }
                except Exception as e:
                    logger.warning(f"Failed to process cached user sessions: {e}")
        
        # קבלה ממסד הנתונים
        try:
            result = self.db.get_user_sessions_paginated(
                user_id=user_id,
                limit=limit,
                offset=offset,
                include_archived=include_archived
            )
            
            sessions = []
            for session_data in result['sessions']:
                session = ChatSession(
                    id=session_data['id'],
                    title=session_data['title'],
                    model_id=session_data['model_id'],
                    user_id=session_data['user_id'],
                    created_at=datetime.fromisoformat(session_data['created_at']),
                    updated_at=datetime.fromisoformat(session_data['updated_at']),
                    message_count=session_data.get('message_count', 0),
                    is_archived=bool(session_data['is_archived']),
                    metadata=json.loads(session_data['metadata']) if session_data['metadata'] else {}
                )
                sessions.append(session)
            
            # שמירה ב-cache (רק לעמוד הראשון)
            if use_cache and offset == 0 and user_id and sessions:
                try:
                    cached_data = [session.to_dict() for session in sessions]
                    self.cache.set_user_sessions(user_id, cached_data, limit)
                except Exception as e:
                    logger.warning(f"Failed to cache user sessions: {e}")
            
            return {
                "sessions": sessions,
                "total_count": result['total_count'],
                "limit": limit,
                "offset": offset,
                "has_more": result['has_more'],
                "from_cache": False
            }
            
        except Exception as e:
            logger.error(f"Failed to list user sessions: {e}")
            return {
                "sessions": [],
                "total_count": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "error": str(e)
            }
    
    def update_session(self, session_id: str, **updates) -> bool:
        """עדכון session"""
        if not updates:
            return False
        
        try:
            # הכנת שדות לעדכון
            fields = []
            values = []
            
            for key, value in updates.items():
                if key == "metadata":
                    value = json.dumps(value)
                fields.append(f"{key} = ?")
                values.append(value)
            
            # הוספת updated_at
            fields.append("updated_at = ?")
            values.append(datetime.utcnow().isoformat())
            values.append(session_id)
            
            # ביצוע עדכון
            cursor = self.db.execute_query(
                f"UPDATE chat_sessions SET {', '.join(fields)} WHERE id = ?",
                tuple(values),
                QueryType.UPDATE
            )
            
            success = cursor.rowcount > 0
            
            if success:
                # ביטול cache
                self.cache.invalidate_session(session_id)
                
                logger.info(f"Updated session {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """מחיקת session"""
        try:
            cursor = self.db.execute_query(
                "DELETE FROM chat_sessions WHERE id = ?",
                (session_id,),
                QueryType.DELETE
            )
            
            success = cursor.rowcount > 0
            
            if success:
                # ביטול cache
                self.cache.invalidate_session(session_id)
                
                logger.info(f"Deleted session {session_id}")
                
                # רישום אירוע audit
                log_user_action(
                    action="session_deleted",
                    session_id=session_id,
                    details={"permanent_deletion": True}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False


# Global instances
optimized_chat_history = OptimizedChatHistoryService()
optimized_session_service = OptimizedSessionService()

# Utility functions
def get_database_performance_summary() -> Dict[str, Any]:
    """קבלת סיכום ביצועי מסד הנתונים"""
    try:
        db_stats = optimized_db.get_performance_stats()
        cache_stats = chat_cache.cache.get_stats()
        
        return {
            "database": {
                "total_queries": db_stats.get('total_queries', 0),
                "avg_execution_time": db_stats.get('avg_execution_time', 0),
                "connection_pool": db_stats.get('connection_pool_stats', {}),
                "recent_errors": len(db_stats.get('recent_errors', []))
            },
            "cache": {
                backend: {
                    "hit_rate": stats.hit_rate,
                    "total_entries": stats.entry_count,
                    "total_size_mb": stats.total_size_bytes / (1024 * 1024)
                }
                for backend, stats in cache_stats.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get performance summary: {e}")
        return {"error": str(e)}

def perform_maintenance(cleanup_days: int = 30, optimize: bool = True) -> Dict[str, Any]:
    """ביצוע תחזוקה של מסד הנתונים"""
    maintenance_results = {}
    
    try:
        # ניקוי נתונים ישנים
        cleanup_stats = optimized_db.cleanup_old_data(days_old=cleanup_days, dry_run=False)
        maintenance_results["cleanup"] = cleanup_stats
        
        # אופטימיזציה
        if optimize:
            optimization_results = optimized_db.optimize_database()
            maintenance_results["optimization"] = optimization_results
        
        # ניקוי cache
        cache_cleared = chat_cache.cache.clear()
        maintenance_results["cache_cleared"] = cache_cleared
        
        maintenance_results["success"] = True
        maintenance_results["timestamp"] = datetime.utcnow().isoformat()
        
        logger.info(f"Database maintenance completed: {maintenance_results}")
        
    except Exception as e:
        logger.error(f"Database maintenance failed: {e}")
        maintenance_results["success"] = False
        maintenance_results["error"] = str(e)
    
    return maintenance_results