"""
בדיקות לשירות Audit Logging
"""

import unittest
import tempfile
import os
import shutil
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.services.security.audit_service import (
    AuditService, AuditEvent, AuditEventType, AuditSeverity,
    log_user_action, log_security_event, log_api_request, get_audit_summary
)


class TestAuditService(unittest.TestCase):
    
    def setUp(self):
        """הכנה לבדיקות"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_audit.db")
        self.service = AuditService(db_path=self.db_path)
        
    def tearDown(self):
        """ניקוי אחרי בדיקות"""
        shutil.rmtree(self.temp_dir)
    
    def test_audit_event_creation(self):
        """בדיקת יצירת אירוע audit"""
        event = AuditEvent(
            event_type=AuditEventType.USER_ACTION,
            action="test_action",
            user_id="user123",
            session_id="session456",
            details={"key": "value"}
        )
        
        self.assertEqual(event.event_type, AuditEventType.USER_ACTION)
        self.assertEqual(event.action, "test_action")
        self.assertEqual(event.user_id, "user123")
        self.assertEqual(event.session_id, "session456")
        self.assertEqual(event.details["key"], "value")
        self.assertTrue(event.success)
    
    def test_audit_event_serialization(self):
        """בדיקת סריאליזציה של אירוע audit"""
        event = AuditEvent(
            event_type=AuditEventType.MESSAGE_SENT,
            action="send_message",
            user_id="user123",
            details={"message_id": "msg456", "content_length": 100}
        )
        
        # המרה למילון
        event_dict = event.to_dict()
        self.assertIn('timestamp', event_dict)
        self.assertEqual(event_dict['event_type'], 'message_sent')
        self.assertEqual(event_dict['action'], 'send_message')
        
        # המרה חזרה לאובייקט
        restored_event = AuditEvent.from_dict(event_dict)
        self.assertEqual(restored_event.event_type, AuditEventType.MESSAGE_SENT)
        self.assertEqual(restored_event.action, "send_message")
        self.assertEqual(restored_event.user_id, "user123")
    
    def test_log_basic_event(self):
        """בדיקת רישום אירוע בסיסי"""
        event_id = self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="test_login",
            user_id="user123",
            details={"ip": "192.168.1.1"}
        )
        
        self.assertIsNotNone(event_id)
        self.assertIsInstance(event_id, str)
        self.assertEqual(len(event_id), 16)  # SHA256 מקוצר
    
    def test_log_event_with_all_fields(self):
        """בדיקת רישום אירוע עם כל השדות"""
        event_id = self.service.log_event(
            event_type=AuditEventType.API_REQUEST,
            action="POST /api/chat/send",
            user_id="user123",
            session_id="session456",
            resource="/api/chat/send",
            details={"method": "POST", "status": 200},
            severity=AuditSeverity.LOW,
            success=True,
            duration_ms=150,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        self.assertIsNotNone(event_id)
        
        # קבלת האירוע חזרה
        events = self.service.get_events(limit=1)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        self.assertEqual(event.action, "POST /api/chat/send")
        self.assertEqual(event.user_id, "user123")
        self.assertEqual(event.session_id, "session456")
        self.assertEqual(event.resource, "/api/chat/send")
        self.assertEqual(event.severity, AuditSeverity.LOW)
        self.assertEqual(event.duration_ms, 150)
        self.assertEqual(event.ip_address, "192.168.1.1")
    
    def test_get_events_basic(self):
        """בדיקת קבלת אירועים בסיסית"""
        # רישום מספר אירועים
        for i in range(5):
            self.service.log_event(
                event_type=AuditEventType.USER_ACTION,
                action=f"action_{i}",
                user_id=f"user_{i}"
            )
        
        # קבלת כל האירועים
        events = self.service.get_events()
        self.assertEqual(len(events), 5)
        
        # בדיקת סדר (האחרון ראשון)
        self.assertEqual(events[0].action, "action_4")
        self.assertEqual(events[4].action, "action_0")
    
    def test_get_events_with_filters(self):
        """בדיקת קבלת אירועים עם פילטרים"""
        # רישום אירועים שונים
        self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="user_login",
            user_id="user1"
        )
        self.service.log_event(
            event_type=AuditEventType.MESSAGE_SENT,
            action="send_message",
            user_id="user2"
        )
        self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="user_logout",
            user_id="user1"
        )
        
        # פילטר לפי משתמש
        user1_events = self.service.get_events(user_id="user1")
        self.assertEqual(len(user1_events), 2)
        
        # פילטר לפי סוג אירוע
        message_events = self.service.get_events(
            event_types=[AuditEventType.MESSAGE_SENT]
        )
        self.assertEqual(len(message_events), 1)
        self.assertEqual(message_events[0].action, "send_message")
    
    def test_get_events_with_date_range(self):
        """בדיקת קבלת אירועים עם טווח תאריכים"""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # רישום אירוע
        self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="test_action",
            user_id="user1"
        )
        
        # בדיקת טווח תאריכים
        events_in_range = self.service.get_events(
            start_date=yesterday,
            end_date=tomorrow
        )
        self.assertEqual(len(events_in_range), 1)
        
        # בדיקת טווח שלא כולל את האירוע
        events_out_of_range = self.service.get_events(
            start_date=tomorrow,
            end_date=tomorrow + timedelta(days=1)
        )
        self.assertEqual(len(events_out_of_range), 0)
    
    def test_get_statistics(self):
        """בדיקת קבלת סטטיסטיקות"""
        # רישום אירועים שונים
        self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="user_action",
            success=True
        )
        self.service.log_event(
            event_type=AuditEventType.API_ERROR,
            action="api_error",
            success=False,
            severity=AuditSeverity.HIGH
        )
        self.service.log_event(
            event_type=AuditEventType.ENCRYPTION_KEY_ROTATED,
            action="key_rotation",
            severity=AuditSeverity.MEDIUM
        )
        
        stats = self.service.get_statistics()
        
        self.assertEqual(stats['total_events'], 3)
        self.assertEqual(stats['error_count'], 1)
        self.assertAlmostEqual(stats['success_rate'], 66.67, places=1)
        
        # בדיקת התפלגות לפי סוג
        self.assertIn('user_action', stats['event_type_distribution'])
        self.assertIn('api_error', stats['event_type_distribution'])
        
        # בדיקת התפלגות לפי חומרה
        self.assertIn('high', stats['severity_distribution'])
        self.assertIn('medium', stats['severity_distribution'])
    
    def test_search_events(self):
        """בדיקת חיפוש אירועים"""
        # רישום אירועים עם תוכן שונה
        self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="login_attempt",
            details={"method": "password"}
        )
        self.service.log_event(
            event_type=AuditEventType.MESSAGE_SENT,
            action="send_message",
            resource="chat_session_123"
        )
        self.service.log_event(
            event_type=AuditEventType.API_ERROR,
            action="api_call",
            error_message="Authentication failed"
        )
        
        # חיפוש לפי action
        login_events = self.service.search_events("login")
        self.assertEqual(len(login_events), 1)
        self.assertEqual(login_events[0].action, "login_attempt")
        
        # חיפוש לפי resource
        chat_events = self.service.search_events("chat_session")
        self.assertEqual(len(chat_events), 1)
        self.assertEqual(chat_events[0].resource, "chat_session_123")
        
        # חיפוש לפי error message
        auth_events = self.service.search_events("Authentication")
        self.assertEqual(len(auth_events), 1)
        self.assertEqual(auth_events[0].error_message, "Authentication failed")
    
    def test_verify_integrity(self):
        """בדיקת אימות שלמות"""
        # רישום אירועים תקינים
        for i in range(3):
            self.service.log_event(
                event_type=AuditEventType.USER_ACTION,
                action=f"action_{i}",
                user_id=f"user_{i}"
            )
        
        # אימות שלמות
        integrity = self.service.verify_integrity()
        
        self.assertTrue(integrity['integrity_ok'])
        self.assertEqual(integrity['total_events'], 3)
        self.assertEqual(integrity['corrupted_events'], 0)
        self.assertEqual(integrity['integrity_percentage'], 100.0)
    
    def test_cleanup_old_logs(self):
        """בדיקת ניקוי לוגים ישנים"""
        # רישום אירוע ישן (סימולציה)
        old_event_id = self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="old_action",
            user_id="user1"
        )
        
        # רישום אירוע חדש
        new_event_id = self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="new_action",
            user_id="user2"
        )
        
        # שינוי תאריך האירוע הישן במסד הנתונים
        import sqlite3
        conn = sqlite3.connect(self.service.db_path)
        cursor = conn.cursor()
        old_date = (datetime.utcnow() - timedelta(days=400)).isoformat()
        cursor.execute(
            "UPDATE audit_events SET timestamp = ? WHERE id = ?",
            (old_date, old_event_id)
        )
        conn.commit()
        conn.close()
        
        # ניקוי לוגים ישנים (מעל 365 יום)
        cleanup_result = self.service.cleanup_old_logs(retention_days=365)
        
        self.assertEqual(cleanup_result['deleted_events'], 1)
        
        # בדיקה שהאירוע החדש נשאר
        remaining_events = self.service.get_events()
        self.assertEqual(len(remaining_events), 1)
        self.assertEqual(remaining_events[0].action, "new_action")
    
    def test_export_logs_json(self):
        """בדיקת ייצוא לוגים בפורמט JSON"""
        # רישום אירועים
        self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="test_action_1",
            user_id="user1"
        )
        self.service.log_event(
            event_type=AuditEventType.MESSAGE_SENT,
            action="test_action_2",
            user_id="user2"
        )
        
        # ייצוא
        exported_json = self.service.export_logs(format="json")
        
        # בדיקת תקינות JSON
        exported_data = json.loads(exported_json)
        self.assertEqual(len(exported_data), 2)
        
        # בדיקת תוכן
        self.assertEqual(exported_data[0]['action'], "test_action_2")  # האחרון ראשון
        self.assertEqual(exported_data[1]['action'], "test_action_1")
    
    def test_export_logs_csv(self):
        """בדיקת ייצוא לוגים בפורמט CSV"""
        # רישום אירוע
        self.service.log_event(
            event_type=AuditEventType.USER_ACTION,
            action="csv_test_action",
            user_id="user1",
            details={"key": "value"}
        )
        
        # ייצוא
        exported_csv = self.service.export_logs(format="csv")
        
        # בדיקת תוכן CSV
        lines = exported_csv.strip().split('\n')
        self.assertGreaterEqual(len(lines), 2)  # כותרת + לפחות שורה אחת
        
        # בדיקת כותרת
        headers = lines[0].split(',')
        self.assertIn('Action', headers)
        self.assertIn('User ID', headers)
        self.assertIn('Event Type', headers)
        
        # בדיקת נתונים
        data_line = lines[1]
        self.assertIn('csv_test_action', data_line)
        self.assertIn('user1', data_line)
    
    def test_concurrent_logging(self):
        """בדיקת רישום במקביל"""
        import threading
        import time
        
        results = []
        errors = []
        
        def log_event(event_num):
            try:
                event_id = self.service.log_event(
                    event_type=AuditEventType.USER_ACTION,
                    action=f"concurrent_action_{event_num}",
                    user_id=f"user_{event_num}"
                )
                results.append(event_id)
            except Exception as e:
                errors.append(str(e))
        
        # יצירת 10 threads לרישום במקביל
        threads = []
        for i in range(10):
            thread = threading.Thread(target=log_event, args=(i,))
            threads.append(thread)
            thread.start()
        
        # המתנה לסיום כל ה-threads
        for thread in threads:
            thread.join()
        
        # בדיקת תוצאות
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10)
        self.assertEqual(len(set(results)), 10)  # כל ה-IDs ייחודיים
        
        # בדיקה שכל האירועים נרשמו
        events = self.service.get_events()
        self.assertEqual(len(events), 10)


class TestAuditServiceHelpers(unittest.TestCase):
    """בדיקות לפונקציות העזר"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_helpers.db")
        
        # יצירת instance חדש לבדיקות
        import backend.services.security.audit_service as audit_module
        self.original_service = audit_module.audit_service
        audit_module.audit_service = audit_module.AuditService(db_path=self.db_path)
    
    def tearDown(self):
        # החזרת השירות המקורי
        import backend.services.security.audit_service as audit_module
        audit_module.audit_service = self.original_service
        shutil.rmtree(self.temp_dir)
    
    def test_log_user_action(self):
        """בדיקת פונקציית log_user_action"""
        event_id = log_user_action(
            action="test_user_action",
            user_id="user123",
            session_id="session456",
            details={"key": "value"}
        )
        
        self.assertIsNotNone(event_id)
        
        # בדיקת האירוע
        import backend.services.security.audit_service as audit_module
        events = audit_module.audit_service.get_events(limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].action, "test_user_action")
        self.assertEqual(events[0].event_type, AuditEventType.USER_ACTION)
    
    def test_log_security_event(self):
        """בדיקת פונקציית log_security_event"""
        event_id = log_security_event(
            action="encryption key rotated",
            severity=AuditSeverity.HIGH,
            user_id="admin",
            details={"old_key": "key1", "new_key": "key2"}
        )
        
        self.assertIsNotNone(event_id)
        
        # בדיקת האירוע
        import backend.services.security.audit_service as audit_module
        events = audit_module.audit_service.get_events(limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, AuditEventType.ENCRYPTION_KEY_ROTATED)
        self.assertEqual(events[0].severity, AuditSeverity.HIGH)
    
    def test_log_api_request(self):
        """בדיקת פונקציית log_api_request"""
        event_id = log_api_request(
            action="GET /api/chat/sessions",
            user_id="user123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            duration_ms=250,
            success=True
        )
        
        self.assertIsNotNone(event_id)
        
        # בדיקת האירוע
        import backend.services.security.audit_service as audit_module
        events = audit_module.audit_service.get_events(limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, AuditEventType.API_REQUEST)
        self.assertEqual(events[0].duration_ms, 250)
        self.assertEqual(events[0].ip_address, "192.168.1.1")
    
    def test_get_audit_summary(self):
        """בדיקת פונקציית get_audit_summary"""
        # רישום מספר אירועים
        log_user_action("action1", "user1")
        log_security_event("security_action", AuditSeverity.MEDIUM)
        log_api_request("api_call", success=False, error_message="Error")
        
        summary = get_audit_summary()
        
        self.assertIn('total_events', summary)
        self.assertIn('error_count', summary)
        self.assertIn('success_rate', summary)
        self.assertEqual(summary['total_events'], 3)
        self.assertEqual(summary['error_count'], 1)


class TestAuditEventTypes(unittest.TestCase):
    """בדיקות לסוגי אירועי audit"""
    
    def test_event_type_values(self):
        """בדיקת ערכי סוגי האירועים"""
        self.assertEqual(AuditEventType.USER_LOGIN.value, "user_login")
        self.assertEqual(AuditEventType.MESSAGE_SENT.value, "message_sent")
        self.assertEqual(AuditEventType.ENCRYPTION_KEY_ROTATED.value, "encryption_key_rotated")
        self.assertEqual(AuditEventType.API_REQUEST.value, "api_request")
    
    def test_severity_values(self):
        """בדיקת ערכי רמות החומרה"""
        self.assertEqual(AuditSeverity.LOW.value, "low")
        self.assertEqual(AuditSeverity.MEDIUM.value, "medium")
        self.assertEqual(AuditSeverity.HIGH.value, "high")
        self.assertEqual(AuditSeverity.CRITICAL.value, "critical")


if __name__ == '__main__':
    unittest.main()