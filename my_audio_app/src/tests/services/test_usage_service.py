import unittest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.usage_service import UsageService
from models.llm_models import UsageRecord


class TestUsageService(unittest.TestCase):
    """בדיקות יחידה לשירות מעקב שימוש"""
    
    def setUp(self):
        """הכנה לפני כל בדיקה"""
        # יצירת קובץ מסד נתונים זמני
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # יצירת שירות עם מסד נתונים זמני
        self.usage_service = UsageService(db_path=self.temp_db.name)
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        # מחיקת קובץ מסד הנתונים הזמני
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_init_creates_default_limits(self):
        """בדיקה שהשירות יוצר מגבלות ברירת מחדל"""
        limits = self.usage_service.get_all_usage_limits()
        
        # בדיקה שיש מגבלות ברירת מחדל
        self.assertGreater(len(limits), 0)
        
        # בדיקה שיש מגבלות מוכרות
        self.assertIn("daily_cost", limits)
        self.assertIn("monthly_cost", limits)
        self.assertIn("daily_tokens", limits)
        self.assertIn("monthly_tokens", limits)
        self.assertIn("hourly_requests", limits)
    
    def test_record_usage(self):
        """בדיקת רישום שימוש"""
        # יצירת רשומת שימוש
        usage_record = UsageRecord(
            id="test-usage-1",
            timestamp=datetime.now(),
            model_id="test-model",
            provider="TestProvider",
            tokens_used=1000,
            cost=0.03,
            response_time=1.5,
            success=True,
            request_type="chat"
        )
        
        # רישום השימוש
        self.usage_service.record_usage(usage_record)
        
        # קבלת רשומות השימוש
        records = self.usage_service.get_usage_records(limit=1)
        
        # בדיקות
        self.assertEqual(len(records), 1)
        retrieved_record = records[0]
        self.assertEqual(retrieved_record.id, usage_record.id)
        self.assertEqual(retrieved_record.model_id, usage_record.model_id)
        self.assertEqual(retrieved_record.provider, usage_record.provider)
        self.assertEqual(retrieved_record.tokens_used, usage_record.tokens_used)
        self.assertEqual(retrieved_record.cost, usage_record.cost)
        self.assertEqual(retrieved_record.success, usage_record.success)
    
    def test_get_usage_records_with_filters(self):
        """בדיקת קבלת רשומות שימוש עם פילטרים"""
        now = datetime.now()
        
        # יצירת מספר רשומות שימוש
        records = [
            UsageRecord(
                id="record-1",
                timestamp=now - timedelta(hours=1),
                model_id="model-1",
                provider="Provider1",
                tokens_used=500,
                cost=0.015,
                response_time=1.0,
                success=True
            ),
            UsageRecord(
                id="record-2",
                timestamp=now - timedelta(hours=2),
                model_id="model-2",
                provider="Provider2",
                tokens_used=1000,
                cost=0.03,
                response_time=2.0,
                success=False
            ),
            UsageRecord(
                id="record-3",
                timestamp=now - timedelta(days=1),
                model_id="model-1",
                provider="Provider1",
                tokens_used=750,
                cost=0.0225,
                response_time=1.5,
                success=True
            )
        ]
        
        # רישום כל הרשומות
        for record in records:
            self.usage_service.record_usage(record)
        
        # בדיקת פילטר לפי ספק
        provider1_records = self.usage_service.get_usage_records(provider="Provider1")
        self.assertEqual(len(provider1_records), 2)
        
        # בדיקת פילטר לפי מודל
        model1_records = self.usage_service.get_usage_records(model_id="model-1")
        self.assertEqual(len(model1_records), 2)
        
        # בדיקת פילטר לפי הצלחה
        success_records = self.usage_service.get_usage_records(success_only=True)
        self.assertEqual(len(success_records), 2)
        
        # בדיקת פילטר לפי תאריך
        recent_records = self.usage_service.get_usage_records(
            start_date=now - timedelta(hours=3)
        )
        self.assertEqual(len(recent_records), 2)
        
        # בדיקת מגבלת מספר רשומות
        limited_records = self.usage_service.get_usage_records(limit=1)
        self.assertEqual(len(limited_records), 1)
    
    def test_get_usage_summary(self):
        """בדיקת קבלת סיכום שימוש"""
        now = datetime.now()
        
        # יצירת רשומות שימוש
        records = [
            UsageRecord(
                id="summary-1",
                timestamp=now,
                model_id="model-1",
                provider="Provider1",
                tokens_used=1000,
                cost=0.03,
                response_time=1.0,
                success=True
            ),
            UsageRecord(
                id="summary-2",
                timestamp=now,
                model_id="model-2",
                provider="Provider2",
                tokens_used=2000,
                cost=0.06,
                response_time=2.0,
                success=True
            ),
            UsageRecord(
                id="summary-3",
                timestamp=now,
                model_id="model-1",
                provider="Provider1",
                tokens_used=500,
                cost=0.015,
                response_time=0.5,
                success=False
            )
        ]
        
        # רישום כל הרשומות
        for record in records:
            self.usage_service.record_usage(record)
        
        # קבלת סיכום
        summary = self.usage_service.get_usage_summary(
            start_date=now.date(),
            end_date=now.date()
        )
        
        # בדיקות
        self.assertEqual(summary["total_requests"], 3)
        self.assertEqual(summary["total_tokens"], 3500)
        self.assertEqual(summary["total_cost"], 0.105)
        self.assertEqual(summary["success_rate"], 2/3)  # 2 מתוך 3 הצליחו
        self.assertEqual(summary["unique_providers"], 2)
        self.assertEqual(summary["unique_models"], 2)
        
        # בדיקת ממוצע זמן תגובה
        expected_avg_response_time = (1.0 + 2.0 + 0.5) / 3
        self.assertAlmostEqual(summary["avg_response_time"], expected_avg_response_time, places=2)
    
    def test_get_usage_by_provider(self):
        """בדיקת קבלת שימוש לפי ספק"""
        now = datetime.now()
        
        # יצירת רשומות שימוש לספקים שונים
        records = [
            UsageRecord(
                id="provider-1-1",
                timestamp=now,
                model_id="model-1",
                provider="Provider1",
                tokens_used=1000,
                cost=0.03,
                response_time=1.0,
                success=True
            ),
            UsageRecord(
                id="provider-1-2",
                timestamp=now,
                model_id="model-2",
                provider="Provider1",
                tokens_used=500,
                cost=0.015,
                response_time=0.8,
                success=True
            ),
            UsageRecord(
                id="provider-2-1",
                timestamp=now,
                model_id="model-3",
                provider="Provider2",
                tokens_used=2000,
                cost=0.06,
                response_time=2.0,
                success=False
            )
        ]
        
        # רישום כל הרשומות
        for record in records:
            self.usage_service.record_usage(record)
        
        # קבלת שימוש לפי ספק
        usage_by_provider = self.usage_service.get_usage_by_provider(
            start_date=now.date(),
            end_date=now.date()
        )
        
        # בדיקות
        self.assertIn("Provider1", usage_by_provider)
        self.assertIn("Provider2", usage_by_provider)
        
        # בדיקת נתוני Provider1
        provider1_data = usage_by_provider["Provider1"]
        self.assertEqual(provider1_data["total_requests"], 2)
        self.assertEqual(provider1_data["total_tokens"], 1500)
        self.assertEqual(provider1_data["total_cost"], 0.045)
        self.assertEqual(provider1_data["success_rate"], 1.0)  # כל הבקשות הצליחו
        
        # בדיקת נתוני Provider2
        provider2_data = usage_by_provider["Provider2"]
        self.assertEqual(provider2_data["total_requests"], 1)
        self.assertEqual(provider2_data["total_tokens"], 2000)
        self.assertEqual(provider2_data["total_cost"], 0.06)
        self.assertEqual(provider2_data["success_rate"], 0.0)  # הבקשה נכשלה
    
    def test_get_usage_trends(self):
        """בדיקת קבלת מגמות שימוש"""
        now = datetime.now()
        
        # יצירת רשומות שימוש במספר ימים
        for days_ago in range(5):
            date = now - timedelta(days=days_ago)
            for i in range(2):  # 2 רשומות ליום
                record = UsageRecord(
                    id=f"trend-{days_ago}-{i}",
                    timestamp=date,
                    model_id="model-1",
                    provider="Provider1",
                    tokens_used=1000,
                    cost=0.03,
                    response_time=1.0,
                    success=True
                )
                self.usage_service.record_usage(record)
        
        # קבלת מגמות
        trends = self.usage_service.get_usage_trends(days=7)
        
        # בדיקות
        self.assertGreater(len(trends), 0)
        
        # בדיקה שכל יום יש לו נתונים
        for trend in trends:
            self.assertIn("date", trend)
            self.assertIn("requests", trend)
            self.assertIn("tokens", trend)
            self.assertIn("cost", trend)
            self.assertIn("success_rate", trend)
    
    def test_set_and_get_usage_limit(self):
        """בדיקת הגדרה וקבלת מגבלת שימוש"""
        limit_type = "test_limit"
        limit_value = 100.0
        warning_threshold = 0.9
        
        # הגדרת מגבלה
        self.usage_service.set_usage_limit(
            limit_type, limit_value, warning_threshold, is_enabled=True
        )
        
        # קבלת המגבלה
        limit_info = self.usage_service.get_usage_limit(limit_type)
        
        # בדיקות
        self.assertIsNotNone(limit_info)
        self.assertEqual(limit_info["limit_type"], limit_type)
        self.assertEqual(limit_info["limit_value"], limit_value)
        self.assertEqual(limit_info["warning_threshold"], warning_threshold)
        self.assertTrue(limit_info["is_enabled"])
    
    def test_get_nonexistent_usage_limit(self):
        """בדיקת קבלת מגבלת שימוש שלא קיימת"""
        limit_info = self.usage_service.get_usage_limit("nonexistent_limit")
        self.assertIsNone(limit_info)
    
    def test_cleanup_old_records(self):
        """בדיקת ניקוי רשומות ישנות"""
        now = datetime.now()
        
        # יצירת רשומות ישנות וחדשות
        old_record = UsageRecord(
            id="old-record",
            timestamp=now - timedelta(days=100),  # רשומה ישנה
            model_id="model-1",
            provider="Provider1",
            tokens_used=1000,
            cost=0.03,
            response_time=1.0,
            success=True
        )
        
        new_record = UsageRecord(
            id="new-record",
            timestamp=now,  # רשומה חדשה
            model_id="model-1",
            provider="Provider1",
            tokens_used=1000,
            cost=0.03,
            response_time=1.0,
            success=True
        )
        
        # רישום הרשומות
        self.usage_service.record_usage(old_record)
        self.usage_service.record_usage(new_record)
        
        # וידוא שיש 2 רשומות
        all_records = self.usage_service.get_usage_records()
        self.assertEqual(len(all_records), 2)
        
        # ניקוי רשומות ישנות (שמירת 30 ימים)
        deleted_count = self.usage_service.cleanup_old_records(days_to_keep=30)
        
        # בדיקות
        self.assertEqual(deleted_count, 1)  # רשומה אחת נמחקה
        
        # וידוא שנשארה רק הרשומה החדשה
        remaining_records = self.usage_service.get_usage_records()
        self.assertEqual(len(remaining_records), 1)
        self.assertEqual(remaining_records[0].id, "new-record")
    
    def test_signals_emitted(self):
        """בדיקת שליחת אותות"""
        # רישום לאותות
        usage_recorded_signal = MagicMock()
        
        self.usage_service.usage_recorded.connect(usage_recorded_signal)
        
        # יצירת רשומת שימוש
        usage_record = UsageRecord(
            id="signal-test",
            timestamp=datetime.now(),
            model_id="test-model",
            provider="TestProvider",
            tokens_used=1000,
            cost=0.03,
            response_time=1.0,
            success=True
        )
        
        # רישום השימוש (אמור לשלוח אות)
        self.usage_service.record_usage(usage_record)
        
        # בדיקת שליחת אות
        usage_recorded_signal.assert_called_once_with(usage_record)
    
    def test_usage_limit_signals(self):
        """בדיקת אותות מגבלות שימוש"""
        # רישום לאותות
        limit_reached_signal = MagicMock()
        warning_signal = MagicMock()
        
        self.usage_service.usage_limit_reached.connect(limit_reached_signal)
        self.usage_service.usage_warning.connect(warning_signal)
        
        # הגדרת מגבלה נמוכה לבדיקה
        self.usage_service.set_usage_limit("daily_cost", 0.05, 0.8)  # מגבלה של $0.05
        
        # יצירת רשומת שימוש שתחרוג מהמגבלה
        usage_record = UsageRecord(
            id="limit-test",
            timestamp=datetime.now(),
            model_id="test-model",
            provider="TestProvider",
            tokens_used=1000,
            cost=0.06,  # מעל המגבלה
            response_time=1.0,
            success=True
        )
        
        # רישום השימוש
        self.usage_service.record_usage(usage_record)
        
        # בדיקת שליחת אות חריגה ממגבלה
        limit_reached_signal.assert_called_once()


if __name__ == "__main__":
    unittest.main()
