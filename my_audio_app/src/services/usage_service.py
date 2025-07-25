import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.llm_models import UsageRecord


class UsageService(QObject):
    """שירות למעקב וניתוח שימוש ב-LLM"""
    
    # אותות
    usage_recorded = pyqtSignal(object)  # UsageRecord
    usage_limit_reached = pyqtSignal(str, float)  # limit_type, current_value
    usage_warning = pyqtSignal(str, float, float)  # limit_type, current_value, limit_value
    
    def __init__(self, db_path: str = None):
        """
        יוצר שירות מעקב שימוש חדש
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים
        """
        super().__init__()
        
        # נתיב למסד הנתונים
        if db_path is None:
            app_data_dir = os.path.join(os.path.expanduser("~"), ".audio_chat_qt")
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, "usage_data.db")
        
        self.db_path = db_path
        
        # הגדרות מגבלות ברירת מחדל
        self.default_limits = {
            "daily_cost": 10.0,  # $10 ליום
            "monthly_cost": 100.0,  # $100 לחודש
            "daily_tokens": 100000,  # 100K טוקנים ליום
            "monthly_tokens": 1000000,  # 1M טוקנים לחודש
            "hourly_requests": 100  # 100 בקשות לשעה
        }
        
        # יצירת מסד נתונים אם לא קיים
        self._init_db()
    
    def _init_db(self) -> None:
        """יצירת מסד נתונים אם לא קיים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת רשומות שימוש
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_records (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            model_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            tokens_used INTEGER NOT NULL,
            cost REAL NOT NULL,
            response_time REAL NOT NULL,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            request_type TEXT DEFAULT 'chat',
            user_id TEXT,
            session_id TEXT,
            metadata TEXT DEFAULT '{}'
        )
        ''')
        
        # טבלת מגבלות שימוש
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_limits (
            limit_type TEXT PRIMARY KEY,
            limit_value REAL NOT NULL,
            warning_threshold REAL DEFAULT 0.8,
            is_enabled BOOLEAN DEFAULT TRUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # טבלת סטטיסטיקות מצטברות (לביצועים)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_stats (
            date TEXT NOT NULL,
            provider TEXT NOT NULL,
            model_id TEXT NOT NULL,
            total_requests INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            total_cost REAL DEFAULT 0.0,
            avg_response_time REAL DEFAULT 0.0,
            success_rate REAL DEFAULT 1.0,
            PRIMARY KEY (date, provider, model_id)
        )
        ''')
        
        # אינדקסים לביצועים
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_records(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_provider ON usage_records(provider)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_model ON usage_records(model_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_success ON usage_records(success)')
        
        conn.commit()
        conn.close()
        
        # יצירת מגבלות ברירת מחדל
        self._init_default_limits()
    
    def _init_default_limits(self) -> None:
        """יצירת מגבלות ברירת מחדל"""
        for limit_type, limit_value in self.default_limits.items():
            if not self.get_usage_limit(limit_type):
                self.set_usage_limit(limit_type, limit_value)
    
    # Usage Recording
    def record_usage(self, usage_record: UsageRecord) -> None:
        """
        רישום שימוש חדש
        
        Args:
            usage_record (UsageRecord): רשומת השימוש
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO usage_records 
        (id, timestamp, model_id, provider, tokens_used, cost, response_time, success,
         error_message, request_type, user_id, session_id, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            usage_record.id,
            usage_record.timestamp.isoformat(),
            usage_record.model_id,
            usage_record.provider,
            usage_record.tokens_used,
            usage_record.cost,
            usage_record.response_time,
            usage_record.success,
            usage_record.error_message,
            usage_record.request_type,
            usage_record.user_id,
            usage_record.session_id,
            json.dumps(usage_record.metadata)
        ))
        
        conn.commit()
        conn.close()
        
        # עדכון סטטיסטיקות יומיות
        self._update_daily_stats(usage_record)
        
        # בדיקת מגבלות
        self._check_limits(usage_record)
        
        # שליחת אות
        self.usage_recorded.emit(usage_record)
    
    def _update_daily_stats(self, usage_record: UsageRecord) -> None:
        """עדכון סטטיסטיקות יומיות"""
        date_str = usage_record.timestamp.date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # בדיקה אם יש רשומה קיימת
        cursor.execute('''
        SELECT total_requests, total_tokens, total_cost, avg_response_time, success_rate
        FROM usage_stats 
        WHERE date = ? AND provider = ? AND model_id = ?
        ''', (date_str, usage_record.provider, usage_record.model_id))
        
        row = cursor.fetchone()
        
        if row:
            # עדכון רשומה קיימת
            total_requests, total_tokens, total_cost, avg_response_time, success_rate = row
            
            new_total_requests = total_requests + 1
            new_total_tokens = total_tokens + usage_record.tokens_used
            new_total_cost = total_cost + usage_record.cost
            
            # חישוב ממוצע זמן תגובה חדש
            new_avg_response_time = ((avg_response_time * total_requests) + usage_record.response_time) / new_total_requests
            
            # חישוב אחוז הצלחה חדש
            success_count = int(success_rate * total_requests) + (1 if usage_record.success else 0)
            new_success_rate = success_count / new_total_requests
            
            cursor.execute('''
            UPDATE usage_stats 
            SET total_requests = ?, total_tokens = ?, total_cost = ?, 
                avg_response_time = ?, success_rate = ?
            WHERE date = ? AND provider = ? AND model_id = ?
            ''', (
                new_total_requests, new_total_tokens, new_total_cost,
                new_avg_response_time, new_success_rate,
                date_str, usage_record.provider, usage_record.model_id
            ))
        else:
            # יצירת רשומה חדשה
            cursor.execute('''
            INSERT INTO usage_stats 
            (date, provider, model_id, total_requests, total_tokens, total_cost,
             avg_response_time, success_rate)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?)
            ''', (
                date_str, usage_record.provider, usage_record.model_id,
                usage_record.tokens_used, usage_record.cost,
                usage_record.response_time, 1.0 if usage_record.success else 0.0
            ))
        
        conn.commit()
        conn.close()
    
    def _check_limits(self, usage_record: UsageRecord) -> None:
        """בדיקת מגבלות שימוש"""
        now = datetime.now()
        
        # בדיקת מגבלות יומיות
        daily_cost = self.get_usage_summary(
            start_date=now.date(),
            end_date=now.date()
        )["total_cost"]
        
        daily_tokens = self.get_usage_summary(
            start_date=now.date(),
            end_date=now.date()
        )["total_tokens"]
        
        # בדיקת מגבלות חודשיות
        month_start = now.replace(day=1).date()
        monthly_cost = self.get_usage_summary(
            start_date=month_start,
            end_date=now.date()
        )["total_cost"]
        
        monthly_tokens = self.get_usage_summary(
            start_date=month_start,
            end_date=now.date()
        )["total_tokens"]
        
        # בדיקת מגבלות שעתיות
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        hourly_requests = len(self.get_usage_records(
            start_date=hour_start,
            end_date=now
        ))
        
        # בדיקת כל מגבלה
        limits_to_check = [
            ("daily_cost", daily_cost),
            ("monthly_cost", monthly_cost),
            ("daily_tokens", daily_tokens),
            ("monthly_tokens", monthly_tokens),
            ("hourly_requests", hourly_requests)
        ]
        
        for limit_type, current_value in limits_to_check:
            limit_info = self.get_usage_limit(limit_type)
            if limit_info and limit_info["is_enabled"]:
                limit_value = limit_info["limit_value"]
                warning_threshold = limit_info["warning_threshold"]
                
                if current_value >= limit_value:
                    self.usage_limit_reached.emit(limit_type, current_value)
                elif current_value >= (limit_value * warning_threshold):
                    self.usage_warning.emit(limit_type, current_value, limit_value)
    
    # Usage Retrieval
    def get_usage_records(self, 
                         start_date: datetime = None,
                         end_date: datetime = None,
                         provider: str = None,
                         model_id: str = None,
                         success_only: bool = None,
                         limit: int = None) -> List[UsageRecord]:
        """
        קבלת רשומות שימוש לפי קריטריונים
        
        Args:
            start_date (datetime, optional): תאריך התחלה
            end_date (datetime, optional): תאריך סיום
            provider (str, optional): ספק מסוים
            model_id (str, optional): מודל מסוים
            success_only (bool, optional): רק רשומות מוצלחות
            limit (int, optional): מגבלת מספר רשומות
        
        Returns:
            List[UsageRecord]: רשימת רשומות שימוש
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # בניית שאילתה
        query = "SELECT * FROM usage_records WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        if model_id:
            query += " AND model_id = ?"
            params.append(model_id)
        
        if success_only is not None:
            query += " AND success = ?"
            params.append(success_only)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # המרת שורות לאובייקטים
        records = []
        for row in rows:
            record = UsageRecord(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                model_id=row[2],
                provider=row[3],
                tokens_used=row[4],
                cost=row[5],
                response_time=row[6],
                success=bool(row[7]),
                error_message=row[8],
                request_type=row[9] or "chat",
                user_id=row[10],
                session_id=row[11],
                metadata=json.loads(row[12]) if row[12] else {}
            )
            records.append(record)
        
        return records
    
    def get_usage_summary(self, 
                         start_date: datetime.date = None,
                         end_date: datetime.date = None,
                         provider: str = None,
                         model_id: str = None) -> Dict[str, Any]:
        """
        קבלת סיכום שימוש
        
        Args:
            start_date (date, optional): תאריך התחלה
            end_date (date, optional): תאריך סיום
            provider (str, optional): ספק מסוים
            model_id (str, optional): מודל מסוים
        
        Returns:
            Dict[str, Any]: סיכום שימוש
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # בניית שאילתה
        query = '''
        SELECT 
            COUNT(*) as total_requests,
            SUM(tokens_used) as total_tokens,
            SUM(cost) as total_cost,
            AVG(response_time) as avg_response_time,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
            COUNT(DISTINCT provider) as unique_providers,
            COUNT(DISTINCT model_id) as unique_models
        FROM usage_records 
        WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND date(timestamp) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date(timestamp) <= ?"
            params.append(end_date.isoformat())
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        if model_id:
            query += " AND model_id = ?"
            params.append(model_id)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        if not row or row[0] == 0:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_response_time": 0.0,
                "success_rate": 0.0,
                "unique_providers": 0,
                "unique_models": 0
            }
        
        total_requests = row[0]
        success_rate = (row[4] / total_requests) if total_requests > 0 else 0.0
        
        return {
            "total_requests": total_requests,
            "total_tokens": row[1] or 0,
            "total_cost": row[2] or 0.0,
            "avg_response_time": row[3] or 0.0,
            "success_rate": success_rate,
            "unique_providers": row[5] or 0,
            "unique_models": row[6] or 0
        }
    
    def get_usage_by_provider(self, 
                             start_date: datetime.date = None,
                             end_date: datetime.date = None) -> Dict[str, Dict[str, Any]]:
        """קבלת שימוש לפי ספק"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
        SELECT 
            provider,
            COUNT(*) as total_requests,
            SUM(tokens_used) as total_tokens,
            SUM(cost) as total_cost,
            AVG(response_time) as avg_response_time,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests
        FROM usage_records 
        WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND date(timestamp) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date(timestamp) <= ?"
            params.append(end_date.isoformat())
        
        query += " GROUP BY provider ORDER BY total_cost DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        result = {}
        for row in rows:
            provider = row[0]
            total_requests = row[1]
            success_rate = (row[5] / total_requests) if total_requests > 0 else 0.0
            
            result[provider] = {
                "total_requests": total_requests,
                "total_tokens": row[2] or 0,
                "total_cost": row[3] or 0.0,
                "avg_response_time": row[4] or 0.0,
                "success_rate": success_rate
            }
        
        return result
    
    def get_usage_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        קבלת מגמות שימוש
        
        Args:
            days (int): מספר ימים אחורה
        
        Returns:
            List[Dict[str, Any]]: נתוני מגמות יומיות
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            date,
            SUM(total_requests) as daily_requests,
            SUM(total_tokens) as daily_tokens,
            SUM(total_cost) as daily_cost,
            AVG(avg_response_time) as daily_avg_response_time,
            AVG(success_rate) as daily_success_rate
        FROM usage_stats 
        WHERE date >= ? AND date <= ?
        GROUP BY date
        ORDER BY date
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        trends = []
        for row in rows:
            trends.append({
                "date": row[0],
                "requests": row[1] or 0,
                "tokens": row[2] or 0,
                "cost": row[3] or 0.0,
                "avg_response_time": row[4] or 0.0,
                "success_rate": row[5] or 0.0
            })
        
        return trends
    
    # Usage Limits Management
    def set_usage_limit(self, limit_type: str, limit_value: float, 
                       warning_threshold: float = 0.8, is_enabled: bool = True) -> None:
        """
        הגדרת מגבלת שימוש
        
        Args:
            limit_type (str): סוג המגבלה
            limit_value (float): ערך המגבלה
            warning_threshold (float): אחוז התראה
            is_enabled (bool): האם המגבלה פעילה
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT OR REPLACE INTO usage_limits 
        (limit_type, limit_value, warning_threshold, is_enabled, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (limit_type, limit_value, warning_threshold, is_enabled, now, now))
        
        conn.commit()
        conn.close()
    
    def get_usage_limit(self, limit_type: str) -> Optional[Dict[str, Any]]:
        """קבלת מגבלת שימוש"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM usage_limits WHERE limit_type = ?', (limit_type,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "limit_type": row[0],
            "limit_value": row[1],
            "warning_threshold": row[2],
            "is_enabled": bool(row[3]),
            "created_at": row[4],
            "updated_at": row[5]
        }
    
    def get_all_usage_limits(self) -> Dict[str, Dict[str, Any]]:
        """קבלת כל מגבלות השימוש"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM usage_limits')
        rows = cursor.fetchall()
        conn.close()
        
        limits = {}
        for row in rows:
            limits[row[0]] = {
                "limit_type": row[0],
                "limit_value": row[1],
                "warning_threshold": row[2],
                "is_enabled": bool(row[3]),
                "created_at": row[4],
                "updated_at": row[5]
            }
        
        return limits
    
    # Data Management
    def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """
        ניקוי רשומות ישנות
        
        Args:
            days_to_keep (int): מספר ימים לשמירה
        
        Returns:
            int: מספר רשומות שנמחקו
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM usage_records WHERE timestamp < ?', (cutoff_date.isoformat(),))
        deleted_count = cursor.rowcount
        
        # ניקוי סטטיסטיקות ישנות
        cursor.execute('DELETE FROM usage_stats WHERE date < ?', (cutoff_date.date().isoformat(),))
        
        conn.commit()
        conn.close()
        
        return deleted_count