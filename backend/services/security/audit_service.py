"""
Audit Logging Service
מספק מערכת מתקדמת לרישום ומעקב אחר כל פעולות המשתמש ואירועי אבטחה
"""

import os
import json
import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
import threading
from contextlib import contextmanager
import ipaddress

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """סוגי אירועי audit"""
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"
    
    # Chat operations
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    SESSION_CREATED = "session_created"
    SESSION_DELETED = "session_deleted"
    SESSION_UPDATED = "session_updated"
    
    # Security events
    ENCRYPTION_KEY_ROTATED = "encryption_key_rotated"
    ENCRYPTION_ENABLED = "encryption_enabled"
    ENCRYPTION_DISABLED = "encryption_disabled"
    DATA_EXPORTED = "data_exported"
    DATA_CLEARED = "data_cleared"
    
    # Privacy events
    PRIVACY_SETTINGS_CHANGED = "privacy_settings_changed"
    LOCAL_ONLY_MODE_ENABLED = "local_only_mode_enabled"
    LOCAL_ONLY_MODE_DISABLED = "local_only_mode_disabled"
    ANONYMOUS_MODE_ENABLED = "anonymous_mode_enabled"
    ANONYMOUS_MODE_DISABLED = "anonymous_mode_disabled"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    ERROR_OCCURRED = "error_occurred"
    WARNING_ISSUED = "warning_issued"
    
    # API events
    API_REQUEST = "api_request"
    API_ERROR = "api_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # File operations
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    FILE_ACCESSED = "file_accessed"


class AuditSeverity(Enum):
    """רמות חומרה של אירועי audit"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """אירוע audit בודד"""
    id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: AuditEventType = AuditEventType.USER_ACTION
    severity: AuditSeverity = AuditSeverity.LOW
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action: str = ""
    resource: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """יצירה ממילון"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['event_type'] = AuditEventType(data['event_type'])
        data['severity'] = AuditSeverity(data['severity'])
        return cls(**data)


class AuditService:
    """
    שירות audit מתקדם לרישום ומעקב אחר פעולות משתמש ואירועי אבטחה
    """
    
    def __init__(self, db_path: str = "data/audit_logs.db", max_log_size_mb: int = 100):
        self.db_path = db_path
        self.max_log_size_mb = max_log_size_mb
        self.max_log_entries = 100000  # מקסימום רשומות לפני ניקוי
        self.retention_days = 365  # שמירת לוגים לשנה
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """אתחול מסד נתונים ללוגי audit"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # טבלת אירועי audit
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                details TEXT DEFAULT '{}',
                success BOOLEAN NOT NULL DEFAULT TRUE,
                error_message TEXT,
                duration_ms INTEGER,
                checksum TEXT NOT NULL
            )
            ''')
            
            # טבלת סטטיסטיקות audit
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_statistics (
                date TEXT PRIMARY KEY,
                total_events INTEGER DEFAULT 0,
                security_events INTEGER DEFAULT 0,
                error_events INTEGER DEFAULT 0,
                user_actions INTEGER DEFAULT 0,
                api_requests INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
            ''')
            
            # אינדקסים לביצועים
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_events (event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_events (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_session_id ON audit_events (session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_events (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_success ON audit_events (success)')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """קבלת חיבור למסד נתונים עם thread safety"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                yield conn
            finally:
                conn.close()
    
    def _generate_event_id(self, event: AuditEvent) -> str:
        """יצירת ID ייחודי לאירוע"""
        content = f"{event.timestamp.isoformat()}{event.event_type.value}{event.action}{event.user_id or ''}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _calculate_checksum(self, event: AuditEvent) -> str:
        """חישוב checksum לאירוע לוודא שלמות"""
        content = json.dumps(event.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def log_event(self, 
                  event_type: AuditEventType,
                  action: str,
                  user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  resource: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  severity: AuditSeverity = AuditSeverity.LOW,
                  success: bool = True,
                  error_message: Optional[str] = None,
                  duration_ms: Optional[int] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None) -> str:
        """רישום אירוע audit"""
        
        try:
            # יצירת אירוע
            event = AuditEvent(
                event_type=event_type,
                action=action,
                user_id=user_id,
                session_id=session_id,
                resource=resource,
                details=details or {},
                severity=severity,
                success=success,
                error_message=error_message,
                duration_ms=duration_ms,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # יצירת ID וchecksum
            event.id = self._generate_event_id(event)
            checksum = self._calculate_checksum(event)
            
            # שמירה במסד נתונים
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO audit_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    event.id,
                    event.timestamp.isoformat(),
                    event.event_type.value,
                    event.severity.value,
                    event.user_id,
                    event.session_id,
                    event.ip_address,
                    event.user_agent,
                    event.action,
                    event.resource,
                    json.dumps(event.details, ensure_ascii=False),
                    event.success,
                    event.error_message,
                    event.duration_ms,
                    checksum
                ))
                conn.commit()
            
            # עדכון סטטיסטיקות
            self._update_statistics(event)
            
            logger.debug(f"Audit event logged: {event.id} - {event.action}")
            return event.id
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # במקרה של כשל, נרשום לפחות ללוג הרגיל
            logger.warning(f"Audit event failed to log: {action} by {user_id}")
            raise
    
    def _update_statistics(self, event: AuditEvent):
        """עדכון סטטיסטיקות יומיות"""
        try:
            date_str = event.timestamp.date().isoformat()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # בדיקה אם קיימת רשומה לתאריך
                cursor.execute('SELECT * FROM audit_statistics WHERE date = ?', (date_str,))
                existing = cursor.fetchone()
                
                if existing:
                    # עדכון רשומה קיימת
                    updates = {
                        'total_events': existing[1] + 1,
                        'security_events': existing[2] + (1 if self._is_security_event(event) else 0),
                        'error_events': existing[3] + (1 if not event.success else 0),
                        'user_actions': existing[4] + (1 if self._is_user_action(event) else 0),
                        'api_requests': existing[5] + (1 if self._is_api_request(event) else 0),
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    
                    cursor.execute('''
                    UPDATE audit_statistics 
                    SET total_events = ?, security_events = ?, error_events = ?, 
                        user_actions = ?, api_requests = ?, last_updated = ?
                    WHERE date = ?
                    ''', (*updates.values(), date_str))
                else:
                    # יצירת רשומה חדשה
                    cursor.execute('''
                    INSERT INTO audit_statistics VALUES (?,?,?,?,?,?,?)
                    ''', (
                        date_str,
                        1,  # total_events
                        1 if self._is_security_event(event) else 0,
                        1 if not event.success else 0,
                        1 if self._is_user_action(event) else 0,
                        1 if self._is_api_request(event) else 0,
                        datetime.utcnow().isoformat()
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update audit statistics: {e}")
    
    def _is_security_event(self, event: AuditEvent) -> bool:
        """בדיקה אם האירוע הוא אירוע אבטחה"""
        security_events = {
            AuditEventType.ENCRYPTION_KEY_ROTATED,
            AuditEventType.ENCRYPTION_ENABLED,
            AuditEventType.ENCRYPTION_DISABLED,
            AuditEventType.DATA_EXPORTED,
            AuditEventType.DATA_CLEARED,
            AuditEventType.PRIVACY_SETTINGS_CHANGED,
            AuditEventType.LOCAL_ONLY_MODE_ENABLED,
            AuditEventType.LOCAL_ONLY_MODE_DISABLED,
            AuditEventType.RATE_LIMIT_EXCEEDED
        }
        return event.event_type in security_events
    
    def _is_user_action(self, event: AuditEvent) -> bool:
        """בדיקה אם האירוע הוא פעולת משתמש"""
        user_actions = {
            AuditEventType.USER_ACTION,
            AuditEventType.MESSAGE_SENT,
            AuditEventType.SESSION_CREATED,
            AuditEventType.SESSION_DELETED,
            AuditEventType.SESSION_UPDATED,
            AuditEventType.FILE_UPLOADED,
            AuditEventType.FILE_DELETED
        }
        return event.event_type in user_actions
    
    def _is_api_request(self, event: AuditEvent) -> bool:
        """בדיקה אם האירוע הוא בקשת API"""
        return event.event_type in {AuditEventType.API_REQUEST, AuditEventType.API_ERROR}
    
    def get_events(self, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   event_types: Optional[List[AuditEventType]] = None,
                   user_id: Optional[str] = None,
                   session_id: Optional[str] = None,
                   severity: Optional[AuditSeverity] = None,
                   success_only: Optional[bool] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[AuditEvent]:
        """קבלת אירועי audit לפי קריטריונים"""
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # בניית שאילתה
                query = "SELECT * FROM audit_events WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if event_types:
                    placeholders = ','.join(['?' for _ in event_types])
                    query += f" AND event_type IN ({placeholders})"
                    params.extend([et.value for et in event_types])
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if session_id:
                    query += " AND session_id = ?"
                    params.append(session_id)
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity.value)
                
                if success_only is not None:
                    query += " AND success = ?"
                    params.append(success_only)
                
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # המרה לאובייקטי AuditEvent
                events = []
                for row in rows:
                    event_data = {
                        'id': row[0],
                        'timestamp': row[1],
                        'event_type': row[2],
                        'severity': row[3],
                        'user_id': row[4],
                        'session_id': row[5],
                        'ip_address': row[6],
                        'user_agent': row[7],
                        'action': row[8],
                        'resource': row[9],
                        'details': json.loads(row[10]) if row[10] else {},
                        'success': bool(row[11]),
                        'error_message': row[12],
                        'duration_ms': row[13]
                    }
                    events.append(AuditEvent.from_dict(event_data))
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
    
    def get_statistics(self, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """קבלת סטטיסטיקות audit"""
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # סטטיסטיקות כלליות
                query = "SELECT COUNT(*) FROM audit_events"
                params = []
                
                if start_date or end_date:
                    query += " WHERE 1=1"
                    if start_date:
                        query += " AND timestamp >= ?"
                        params.append(start_date.isoformat())
                    if end_date:
                        query += " AND timestamp <= ?"
                        params.append(end_date.isoformat())
                
                cursor.execute(query, params)
                total_events = cursor.fetchone()[0]
                
                # סטטיסטיקות לפי סוג אירוע
                query = "SELECT event_type, COUNT(*) FROM audit_events"
                if start_date or end_date:
                    query += " WHERE 1=1"
                    if start_date:
                        query += " AND timestamp >= ?"
                    if end_date:
                        query += " AND timestamp <= ?"
                query += " GROUP BY event_type"
                
                cursor.execute(query, params)
                event_type_stats = dict(cursor.fetchall())
                
                # סטטיסטיקות לפי חומרה
                query = "SELECT severity, COUNT(*) FROM audit_events"
                if start_date or end_date:
                    query += " WHERE 1=1"
                    if start_date:
                        query += " AND timestamp >= ?"
                    if end_date:
                        query += " AND timestamp <= ?"
                query += " GROUP BY severity"
                
                cursor.execute(query, params)
                severity_stats = dict(cursor.fetchall())
                
                # סטטיסטיקות שגיאות
                query = "SELECT COUNT(*) FROM audit_events WHERE success = FALSE"
                if start_date or end_date:
                    if start_date or end_date:
                        query += " AND 1=1"
                        if start_date:
                            query += " AND timestamp >= ?"
                        if end_date:
                            query += " AND timestamp <= ?"
                
                cursor.execute(query, params)
                error_count = cursor.fetchone()[0]
                
                # סטטיסטיקות יומיות
                daily_query = "SELECT * FROM audit_statistics"
                daily_params = []
                
                if start_date or end_date:
                    daily_query += " WHERE 1=1"
                    if start_date:
                        daily_query += " AND date >= ?"
                        daily_params.append(start_date.date().isoformat())
                    if end_date:
                        daily_query += " AND date <= ?"
                        daily_params.append(end_date.date().isoformat())
                
                daily_query += " ORDER BY date DESC"
                cursor.execute(daily_query, daily_params)
                daily_stats = cursor.fetchall()
                
                return {
                    'total_events': total_events,
                    'error_count': error_count,
                    'success_rate': (total_events - error_count) / total_events * 100 if total_events > 0 else 100,
                    'event_type_distribution': event_type_stats,
                    'severity_distribution': severity_stats,
                    'daily_statistics': [
                        {
                            'date': row[0],
                            'total_events': row[1],
                            'security_events': row[2],
                            'error_events': row[3],
                            'user_actions': row[4],
                            'api_requests': row[5],
                            'last_updated': row[6]
                        }
                        for row in daily_stats
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get audit statistics: {e}")
            return {}
    
    def search_events(self, 
                     search_term: str,
                     search_fields: List[str] = None) -> List[AuditEvent]:
        """חיפוש אירועי audit"""
        
        if not search_fields:
            search_fields = ['action', 'resource', 'error_message', 'details']
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # בניית שאילתת חיפוש
                conditions = []
                params = []
                
                for field in search_fields:
                    if field == 'details':
                        conditions.append(f"{field} LIKE ?")
                        params.append(f"%{search_term}%")
                    else:
                        conditions.append(f"{field} LIKE ?")
                        params.append(f"%{search_term}%")
                
                query = f"SELECT * FROM audit_events WHERE {' OR '.join(conditions)} ORDER BY timestamp DESC LIMIT 100"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # המרה לאובייקטי AuditEvent
                events = []
                for row in rows:
                    event_data = {
                        'id': row[0],
                        'timestamp': row[1],
                        'event_type': row[2],
                        'severity': row[3],
                        'user_id': row[4],
                        'session_id': row[5],
                        'ip_address': row[6],
                        'user_agent': row[7],
                        'action': row[8],
                        'resource': row[9],
                        'details': json.loads(row[10]) if row[10] else {},
                        'success': bool(row[11]),
                        'error_message': row[12],
                        'duration_ms': row[13]
                    }
                    events.append(AuditEvent.from_dict(event_data))
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to search audit events: {e}")
            return []
    
    def verify_integrity(self) -> Dict[str, Any]:
        """אימות שלמות לוגי audit"""
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # בדיקת כל הרשומות
                cursor.execute("SELECT * FROM audit_events")
                rows = cursor.fetchall()
                
                total_events = len(rows)
                corrupted_events = 0
                corrupted_ids = []
                
                for row in rows:
                    try:
                        # יצירת אירוע מהנתונים
                        event_data = {
                            'id': row[0],
                            'timestamp': row[1],
                            'event_type': row[2],
                            'severity': row[3],
                            'user_id': row[4],
                            'session_id': row[5],
                            'ip_address': row[6],
                            'user_agent': row[7],
                            'action': row[8],
                            'resource': row[9],
                            'details': json.loads(row[10]) if row[10] else {},
                            'success': bool(row[11]),
                            'error_message': row[12],
                            'duration_ms': row[13]
                        }
                        
                        event = AuditEvent.from_dict(event_data)
                        stored_checksum = row[14]
                        calculated_checksum = self._calculate_checksum(event)
                        
                        if stored_checksum != calculated_checksum:
                            corrupted_events += 1
                            corrupted_ids.append(row[0])
                            
                    except Exception as e:
                        corrupted_events += 1
                        corrupted_ids.append(row[0])
                        logger.warning(f"Corrupted audit event {row[0]}: {e}")
                
                return {
                    'total_events': total_events,
                    'corrupted_events': corrupted_events,
                    'integrity_percentage': (total_events - corrupted_events) / total_events * 100 if total_events > 0 else 100,
                    'corrupted_event_ids': corrupted_ids[:10],  # רק 10 הראשונים
                    'integrity_ok': corrupted_events == 0
                }
                
        except Exception as e:
            logger.error(f"Failed to verify audit integrity: {e}")
            return {'integrity_ok': False, 'error': str(e)}
    
    def cleanup_old_logs(self, retention_days: int = None) -> Dict[str, int]:
        """ניקוי לוגים ישנים"""
        
        if retention_days is None:
            retention_days = self.retention_days
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # מחיקת אירועים ישנים
                cursor.execute(
                    "DELETE FROM audit_events WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                deleted_events = cursor.rowcount
                
                # מחיקת סטטיסטיקות ישנות
                cursor.execute(
                    "DELETE FROM audit_statistics WHERE date < ?",
                    (cutoff_date.date().isoformat(),)
                )
                deleted_stats = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_events} old audit events and {deleted_stats} statistics")
                
                return {
                    'deleted_events': deleted_events,
                    'deleted_statistics': deleted_stats
                }
                
        except Exception as e:
            logger.error(f"Failed to cleanup old audit logs: {e}")
            return {'deleted_events': 0, 'deleted_statistics': 0}
    
    def rotate_logs(self) -> bool:
        """רוטציה של לוגים כאשר הם גדולים מדי"""
        
        try:
            # בדיקת גודל קובץ מסד הנתונים
            if os.path.exists(self.db_path):
                file_size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
                
                if file_size_mb > self.max_log_size_mb:
                    logger.info(f"Audit log file size ({file_size_mb:.2f}MB) exceeds limit ({self.max_log_size_mb}MB)")
                    
                    # ניקוי אוטומטי של לוגים ישנים
                    cleanup_result = self.cleanup_old_logs(retention_days=30)  # ניקוי לוגים מעל 30 יום
                    
                    if cleanup_result['deleted_events'] > 0:
                        logger.info(f"Rotated audit logs: deleted {cleanup_result['deleted_events']} old events")
                        return True
                    else:
                        logger.warning("Log rotation needed but no old events found to delete")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate audit logs: {e}")
            return False
    
    def export_logs(self, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   format: str = "json") -> str:
        """ייצוא לוגי audit"""
        
        try:
            events = self.get_events(
                start_date=start_date,
                end_date=end_date,
                limit=10000  # מגבלה גבוהה לייצוא
            )
            
            if format == "json":
                return json.dumps([event.to_dict() for event in events], ensure_ascii=False, indent=2)
            elif format == "csv":
                return self._export_to_csv(events)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export audit logs: {e}")
            raise
    
    def _export_to_csv(self, events: List[AuditEvent]) -> str:
        """ייצוא לפורמט CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # כותרות
        headers = [
            'ID', 'Timestamp', 'Event Type', 'Severity', 'User ID', 'Session ID',
            'IP Address', 'User Agent', 'Action', 'Resource', 'Success', 
            'Error Message', 'Duration (ms)', 'Details'
        ]
        writer.writerow(headers)
        
        # נתונים
        for event in events:
            writer.writerow([
                event.id,
                event.timestamp.isoformat(),
                event.event_type.value,
                event.severity.value,
                event.user_id or '',
                event.session_id or '',
                event.ip_address or '',
                event.user_agent or '',
                event.action,
                event.resource or '',
                'Yes' if event.success else 'No',
                event.error_message or '',
                event.duration_ms or '',
                json.dumps(event.details, ensure_ascii=False) if event.details else ''
            ])
        
        return output.getvalue()


# יצירת instance גלובלי
audit_service = AuditService()


# פונקציות נוחות לשימוש
def log_user_action(action: str, user_id: str = None, session_id: str = None, 
                   details: Dict[str, Any] = None, success: bool = True,
                   error_message: str = None) -> str:
    """רישום פעולת משתמש"""
    return audit_service.log_event(
        event_type=AuditEventType.USER_ACTION,
        action=action,
        user_id=user_id,
        session_id=session_id,
        details=details,
        success=success,
        error_message=error_message
    )


def log_security_event(action: str, severity: AuditSeverity = AuditSeverity.MEDIUM,
                      user_id: str = None, details: Dict[str, Any] = None) -> str:
    """רישום אירוע אבטחה"""
    # קביעת סוג האירוע לפי הפעולה
    event_type = AuditEventType.USER_ACTION
    if 'encryption' in action.lower():
        if 'key' in action.lower() and 'rotat' in action.lower():
            event_type = AuditEventType.ENCRYPTION_KEY_ROTATED
        elif 'enable' in action.lower():
            event_type = AuditEventType.ENCRYPTION_ENABLED
        elif 'disable' in action.lower():
            event_type = AuditEventType.ENCRYPTION_DISABLED
    elif 'export' in action.lower():
        event_type = AuditEventType.DATA_EXPORTED
    elif 'clear' in action.lower() or 'delete' in action.lower():
        event_type = AuditEventType.DATA_CLEARED
    elif 'privacy' in action.lower():
        event_type = AuditEventType.PRIVACY_SETTINGS_CHANGED
    
    return audit_service.log_event(
        event_type=event_type,
        action=action,
        user_id=user_id,
        details=details,
        severity=severity
    )


def log_api_request(action: str, user_id: str = None, ip_address: str = None,
                   user_agent: str = None, duration_ms: int = None,
                   success: bool = True, error_message: str = None) -> str:
    """רישום בקשת API"""
    return audit_service.log_event(
        event_type=AuditEventType.API_REQUEST if success else AuditEventType.API_ERROR,
        action=action,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        duration_ms=duration_ms,
        success=success,
        error_message=error_message,
        severity=AuditSeverity.LOW if success else AuditSeverity.MEDIUM
    )


def get_audit_summary() -> Dict[str, Any]:
    """קבלת סיכום audit"""
    return audit_service.get_statistics()