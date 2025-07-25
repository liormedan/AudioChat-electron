"""
בדיקות יחידה לרכיב UsageMonitor
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QDate

# הוספת נתיב למודלים
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.llm_models import UsageRecord
from services.usage_service import UsageService
from ui.components.llm.usage_monitor import UsageMonitor, StatCard, UsageHistoryTable, UsageLimitsWidget


class TestStatCard(unittest.TestCase):
    """בדיקות לכרטיס סטטיסטיקה"""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לפני כל בדיקה"""
        self.card = StatCard("Test Metric", "100", "📊", "#4CAF50")
    
    def test_initialization(self):
        """בדיקת יצירת כרטיס"""
        self.assertEqual(self.card.title, "Test Metric")
        self.assertEqual(self.card.value, "100")
        self.assertEqual(self.card.icon, "📊")
        self.assertEqual(self.card.color, "#4CAF50")
        
        # בדיקת גודל קבוע
        self.assertEqual(self.card.size().width(), 180)
        self.assertEqual(self.card.size().height(), 120)
    
    def test_update_value(self):
        """בדיקת עדכון ערך"""
        # עדכון ערך בלבד
        self.card.update_value("200")
        self.assertEqual(self.card.value, "200")
        self.assertEqual(self.card.value_label.text(), "200")
        
        # עדכון עם שינוי
        self.card.update_value("300", "+100")
        self.assertEqual(self.card.value, "300")
        self.assertEqual(self.card.change_label.text(), "+100")
        self.assertTrue(self.card.change_label.isVisible())
    
    def test_change_colors(self):
        """בדיקת צבעי שינוי"""
        # שינוי חיובי (אדום)
        self.card.update_value("200", "+50")
        self.assertIn("#F44336", self.card.change_label.styleSheet())
        
        # שינוי שלילי (ירוק)
        self.card.update_value("150", "-50")
        self.assertIn("#4CAF50", self.card.change_label.styleSheet())
        
        # שינוי ניטרלי
        self.card.update_value("150", "stable")
        self.assertIn("#666666", self.card.change_label.styleSheet())


class TestUsageHistoryTable(unittest.TestCase):
    """בדיקות לטבלת היסטוריה"""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לפני כל בדיקה"""
        self.table = UsageHistoryTable()
    
    def test_initialization(self):
        """בדיקת יצירת טבלה"""
        # בדיקת מספר עמודות
        self.assertEqual(self.table.columnCount(), 7)
        
        # בדיקת כותרות עמודות
        expected_headers = ["תאריך", "מודל", "ספק", "טוקנים", "עלות", "זמן תגובה", "סטטוס"]
        for i, header in enumerate(expected_headers):
            self.assertEqual(self.table.horizontalHeaderItem(i).text(), header)
        
        # בדיקת הגדרות טבלה
        self.assertTrue(self.table.alternatingRowColors())
        self.assertTrue(self.table.isSortingEnabled())
    
    def test_load_usage_records(self):
        """בדיקת טעינת רשומות"""
        # יצירת רשומות דמה
        records = [
            UsageRecord(
                id="1",
                timestamp=datetime.now(),
                model_id="gpt-4",
                provider="OpenAI",
                tokens_used=1000,
                cost=0.02,
                response_time=1.5,
                success=True
            ),
            UsageRecord(
                id="2",
                timestamp=datetime.now() - timedelta(hours=1),
                model_id="claude-3",
                provider="Anthropic",
                tokens_used=800,
                cost=0.016,
                response_time=2.1,
                success=False,
                error_message="Rate limit exceeded"
            )
        ]
        
        # טעינת רשומות
        self.table.load_usage_records(records)
        
        # בדיקת מספר שורות
        self.assertEqual(self.table.rowCount(), 2)
        
        # בדיקת תוכן השורה הראשונה
        self.assertEqual(self.table.item(0, 1).text(), "gpt-4")  # מודל
        self.assertEqual(self.table.item(0, 2).text(), "OpenAI")  # ספק
        self.assertEqual(self.table.item(0, 3).text(), "1,000")  # טוקנים
        
        # בדיקת צבע סטטוס
        success_item = self.table.item(0, 6)
        error_item = self.table.item(1, 6)
        
        # הפריט המוצלח צריך להיות ירוק
        self.assertIn("✅", success_item.text())
        
        # הפריט הכושל צריך להיות אדום
        self.assertIn("❌", error_item.text())


class TestUsageLimitsWidget(unittest.TestCase):
    """בדיקות לווידג'ט מגבלות"""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לפני כל בדיקה"""
        self.mock_usage_service = Mock(spec=UsageService)
        self.mock_usage_service.get_all_usage_limits.return_value = {}
        self.widget = UsageLimitsWidget(self.mock_usage_service)
    
    def test_initialization(self):
        """בדיקת יצירת ווידג'ט"""
        # בדיקת ערכי ברירת מחדל
        self.assertEqual(self.widget.daily_cost_spin.value(), 10.0)
        self.assertEqual(self.widget.daily_tokens_spin.value(), 100000)
        self.assertEqual(self.widget.monthly_cost_spin.value(), 100.0)
        self.assertEqual(self.widget.monthly_tokens_spin.value(), 1000000)
        self.assertEqual(self.widget.hourly_requests_spin.value(), 100)
        
        # בדיקת מצב פעיל
        self.assertTrue(self.widget.daily_cost_enabled.isChecked())
        self.assertTrue(self.widget.daily_tokens_enabled.isChecked())
        self.assertTrue(self.widget.monthly_cost_enabled.isChecked())
        self.assertTrue(self.widget.monthly_tokens_enabled.isChecked())
        self.assertTrue(self.widget.hourly_requests_enabled.isChecked())
    
    def test_load_existing_limits(self):
        """בדיקת טעינת מגבלות קיימות"""
        # הגדרת מגבלות דמה
        limits = {
            "daily_cost": {"limit_value": 20.0, "is_enabled": False},
            "daily_tokens": {"limit_value": 50000, "is_enabled": True},
            "monthly_cost": {"limit_value": 200.0, "is_enabled": True}
        }
        
        self.mock_usage_service.get_all_usage_limits.return_value = limits
        
        # יצירת ווידג'ט חדש עם המגבלות
        widget = UsageLimitsWidget(self.mock_usage_service)
        
        # בדיקת טעינת הערכים
        self.assertEqual(widget.daily_cost_spin.value(), 20.0)
        self.assertFalse(widget.daily_cost_enabled.isChecked())
        self.assertEqual(widget.daily_tokens_spin.value(), 50000)
        self.assertTrue(widget.daily_tokens_enabled.isChecked())
        self.assertEqual(widget.monthly_cost_spin.value(), 200.0)
        self.assertTrue(widget.monthly_cost_enabled.isChecked())
    
    def test_limits_changed_signal(self):
        """בדיקת אות שינוי מגבלות"""
        signal_received = False
        received_limits = None
        
        def on_limits_changed(limits):
            nonlocal signal_received, received_limits
            signal_received = True
            received_limits = limits
        
        self.widget.limits_changed.connect(on_limits_changed)
        
        # שינוי ערך
        self.widget.daily_cost_spin.setValue(25.0)
        
        # בדיקת קבלת האות
        self.assertTrue(signal_received)
        self.assertIsNotNone(received_limits)
        self.assertEqual(received_limits["daily_cost"]["value"], 25.0)
    
    def test_save_limits(self):
        """בדיקת שמירת מגבלות"""
        # שינוי ערכים
        self.widget.daily_cost_spin.setValue(15.0)
        self.widget.daily_cost_enabled.setChecked(False)
        
        # שמירה
        self.widget.save_limits()
        
        # בדיקת קריאה לשירות
        self.mock_usage_service.set_usage_limit.assert_called()
        
        # בדיקת הפרמטרים של הקריאה האחרונה
        calls = self.mock_usage_service.set_usage_limit.call_args_list
        daily_cost_call = None
        for call in calls:
            if call[1]["limit_type"] == "daily_cost":
                daily_cost_call = call
                break
        
        self.assertIsNotNone(daily_cost_call)
        self.assertEqual(daily_cost_call[1]["limit_value"], 15.0)
        self.assertFalse(daily_cost_call[1]["is_enabled"])
    
    def test_reset_limits(self):
        """בדיקת איפוס מגבלות"""
        # שינוי ערכים
        self.widget.daily_cost_spin.setValue(50.0)
        self.widget.monthly_cost_spin.setValue(500.0)
        
        # איפוס (נדמה לחיצה על כפתור אישור)
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=16384):  # Yes
            self.widget.reset_limits()
        
        # בדיקת חזרה לערכי ברירת מחדל
        self.assertEqual(self.widget.daily_cost_spin.value(), 10.0)
        self.assertEqual(self.widget.monthly_cost_spin.value(), 100.0)


class TestUsageMonitor(unittest.TestCase):
    """בדיקות לרכיב UsageMonitor"""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """הגדרה לפני כל בדיקה"""
        self.mock_usage_service = Mock(spec=UsageService)
        
        # הגדרת תגובות ברירת מחדל
        self.mock_usage_service.get_usage_summary.return_value = {
            "total_requests": 100,
            "total_tokens": 50000,
            "total_cost": 5.0,
            "avg_response_time": 1.2,
            "success_rate": 0.95,
            "unique_providers": 2,
            "unique_models": 3
        }
        
        self.mock_usage_service.get_usage_records.return_value = []
        self.mock_usage_service.get_usage_trends.return_value = []
        self.mock_usage_service.get_usage_by_provider.return_value = {}
        self.mock_usage_service.get_all_usage_limits.return_value = {}
        self.mock_usage_service.get_usage_limit.return_value = None
        
        # יצירת הרכיב עם השירות המדומה
        self.monitor = UsageMonitor(self.mock_usage_service)
    
    def test_initialization(self):
        """בדיקת יצירת המוניטור"""
        # בדיקת יצירת טאבים
        self.assertEqual(self.monitor.tab_widget.count(), 3)
        
        # בדיקת שמות טאבים
        tab_names = []
        for i in range(self.monitor.tab_widget.count()):
            tab_names.append(self.monitor.tab_widget.tabText(i))
        
        self.assertIn("📊 סקירה כללית", tab_names)
        self.assertIn("📋 היסטוריה", tab_names)
        self.assertIn("⚠️ מגבלות", tab_names)
        
        # בדיקת יצירת כרטיסי סטטיסטיקה
        self.assertIsNotNone(self.monitor.tokens_card)
        self.assertIsNotNone(self.monitor.calls_card)
        self.assertIsNotNone(self.monitor.cost_card)
        self.assertIsNotNone(self.monitor.errors_card)
        
        # בדיקת יצירת גרפים
        self.assertIsNotNone(self.monitor.usage_chart)
        self.assertIsNotNone(self.monitor.providers_chart)
        
        # בדיקת יצירת טבלת היסטוריה
        self.assertIsNotNone(self.monitor.history_table)
        
        # בדיקת יצירת ווידג'ט מגבלות
        self.assertIsNotNone(self.monitor.limits_widget)
    
    def test_refresh_data(self):
        """בדיקת רענון נתונים"""
        # קריאה לרענון
        self.monitor.refresh_data()
        
        # בדיקת קריאות לשירות
        self.mock_usage_service.get_usage_summary.assert_called()
        self.mock_usage_service.get_usage_records.assert_called()
        self.mock_usage_service.get_usage_trends.assert_called()
        self.mock_usage_service.get_usage_by_provider.assert_called()
    
    def test_update_overview_stats(self):
        """בדיקת עדכון סטטיסטיקות"""
        # הגדרת נתונים דמה
        daily_stats = {
            "total_requests": 10,
            "total_tokens": 5000,
            "total_cost": 0.5,
            "avg_response_time": 1.0,
            "success_rate": 1.0,
            "unique_providers": 1,
            "unique_models": 1
        }
        
        monthly_stats = {
            "total_requests": 100,
            "total_tokens": 50000,
            "total_cost": 5.0,
            "avg_response_time": 1.2,
            "success_rate": 0.95,
            "unique_providers": 2,
            "unique_models": 3
        }
        
        # הגדרת תגובות השירות
        def get_usage_summary_side_effect(start_date, end_date):
            if start_date == end_date:  # יומי
                return daily_stats
            else:  # חודשי
                return monthly_stats
        
        self.mock_usage_service.get_usage_summary.side_effect = get_usage_summary_side_effect
        
        # עדכון סטטיסטיקות
        self.monitor.update_overview_stats()
        
        # בדיקת עדכון כרטיסים
        self.assertEqual(self.monitor.tokens_card.value_label.text(), "50,000")
        self.assertEqual(self.monitor.calls_card.value_label.text(), "100")
        self.assertEqual(self.monitor.cost_card.value_label.text(), "$5.00")
        
        # בדיקת עדכון פרטים נוספים
        self.assertEqual(self.monitor.avg_response_time_label.text(), "1.20s")
        self.assertEqual(self.monitor.success_rate_label.text(), "95.0%")
        self.assertEqual(self.monitor.active_providers_label.text(), "2")
        self.assertEqual(self.monitor.active_models_label.text(), "3")
    
    def test_filter_history(self):
        """בדיקת פילטור היסטוריה"""
        # יצירת רשומות דמה
        now = datetime.now()
        records = [
            UsageRecord(
                id="1",
                timestamp=now,
                model_id="gpt-4",
                provider="OpenAI",
                tokens_used=1000,
                cost=0.02,
                response_time=1.5,
                success=True
            ),
            UsageRecord(
                id="2",
                timestamp=now - timedelta(days=2),
                model_id="claude-3",
                provider="Anthropic",
                tokens_used=800,
                cost=0.016,
                response_time=2.1,
                success=False
            ),
            UsageRecord(
                id="3",
                timestamp=now - timedelta(days=5),
                model_id="gpt-3.5",
                provider="OpenAI",
                tokens_used=500,
                cost=0.001,
                response_time=0.8,
                success=True
            )
        ]
        
        self.monitor.usage_records = records
        
        # הגדרת פילטר תאריכים (3 ימים אחרונים)
        self.monitor.date_from.setDate(QDate.currentDate().addDays(-3))
        self.monitor.date_to.setDate(QDate.currentDate())
        
        # הגדרת פילטר ספק
        self.monitor.provider_filter.clear()
        self.monitor.provider_filter.addItems(["כל הספקים", "OpenAI", "Anthropic"])
        self.monitor.provider_filter.setCurrentText("OpenAI")
        
        # הגדרת פילטר סטטוס
        self.monitor.status_filter.setCurrentText("הצליח")
        
        # ביצוע פילטור
        self.monitor.filter_history()
        
        # בדיקת תוצאות - צריכה להיות רק רשומה אחת (OpenAI, מוצלח, בטווח התאריכים)
        self.assertEqual(self.monitor.history_table.rowCount(), 1)
        self.assertEqual(self.monitor.history_table.item(0, 1).text(), "gpt-4")
        self.assertEqual(self.monitor.history_table.item(0, 2).text(), "OpenAI")
    
    def test_usage_limit_signals(self):
        """בדיקת אותות מגבלות שימוש"""
        # בדיקת אות חריגה ממגבלה
        limit_exceeded_received = False
        
        def on_limit_exceeded(limit_type, current, limit):
            nonlocal limit_exceeded_received
            limit_exceeded_received = True
        
        self.monitor.usage_limit_exceeded.connect(on_limit_exceeded)
        
        # הדמיית חריגה ממגבלה
        self.monitor.on_limit_reached("daily_cost", 15.0)
        
        # בדיקת קבלת האות
        self.assertTrue(limit_exceeded_received)
        
        # בדיקת אות אזהרה
        warning_received = False
        
        def on_warning(limit_type, current, limit):
            nonlocal warning_received
            warning_received = True
        
        self.monitor.usage_limit_warning.connect(on_warning)
        
        # הדמיית אזהרה
        self.monitor.on_usage_warning("daily_cost", 8.0, 10.0)
        
        # בדיקת קבלת האות
        self.assertTrue(warning_received)
    
    def test_export_history(self):
        """בדיקת ייצוא היסטוריה"""
        # יצירת רשומות דמה
        records = [
            UsageRecord(
                id="1",
                timestamp=datetime.now(),
                model_id="gpt-4",
                provider="OpenAI",
                tokens_used=1000,
                cost=0.02,
                response_time=1.5,
                success=True
            )
        ]
        
        self.monitor.usage_records = records
        
        # דמיית בחירת קובץ
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', 
                  return_value=('/tmp/test_export.csv', 'CSV Files (*.csv)')):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                # ביצוע ייצוא
                self.monitor.export_history()
                
                # בדיקת פתיחת הקובץ
                mock_open.assert_called_once()
    
    def tearDown(self):
        """ניקוי אחרי כל בדיקה"""
        if hasattr(self, 'monitor'):
            self.monitor.update_timer.stop()
            self.monitor.close()


if __name__ == '__main__':
    unittest.main()
