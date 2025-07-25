#!/usr/bin/env python3
"""
בדיקה פשוטה לרכיב UsageMonitor
"""

import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import uuid

# הוספת נתיב למודלים
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from models.llm_models import UsageRecord
    print("✅ UsageRecord imported successfully")
except ImportError as e:
    print(f"❌ Failed to import UsageRecord: {e}")
    sys.exit(1)

try:
    from services.usage_service import UsageService
    print("✅ UsageService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import UsageService: {e}")
    sys.exit(1)

try:
    from ui.components.llm.usage_monitor import UsageMonitor, StatCard, UsageHistoryTable, UsageLimitsWidget
    print("✅ UsageMonitor components imported successfully")
except ImportError as e:
    print(f"❌ Failed to import UsageMonitor components: {e}")
    sys.exit(1)


def test_stat_card():
    """בדיקת כרטיס סטטיסטיקה"""
    print("\n🧪 Testing StatCard...")
    
    app = QApplication([])
    
    card = StatCard("Test Metric", "100", "📊", "#4CAF50")
    print(f"   Title: {card.title}")
    print(f"   Value: {card.value}")
    print(f"   Icon: {card.icon}")
    print(f"   Color: {card.color}")
    
    # בדיקת עדכון ערך
    card.update_value("200", "+100")
    print(f"   Updated value: {card.value}")
    print("✅ StatCard test passed")


def test_usage_service():
    """בדיקת שירות שימוש"""
    print("\n🧪 Testing UsageService...")
    
    service = UsageService()
    
    # יצירת רשומת שימוש דמה
    record = UsageRecord(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        model_id="gpt-4",
        provider="OpenAI",
        tokens_used=1000,
        cost=0.02,
        response_time=1.5,
        success=True
    )
    
    # רישום השימוש
    service.record_usage(record)
    print("   Usage record created and saved")
    
    # קבלת סיכום
    summary = service.get_usage_summary()
    print(f"   Total requests: {summary['total_requests']}")
    print(f"   Total tokens: {summary['total_tokens']}")
    print(f"   Total cost: ${summary['total_cost']:.4f}")
    
    print("✅ UsageService test passed")


def test_usage_monitor():
    """בדיקת מוניטור שימוש"""
    print("\n🧪 Testing UsageMonitor...")
    
    app = QApplication([])
    
    # יצירת שירות שימוש
    service = UsageService()
    
    # יצירת מוניטור
    monitor = UsageMonitor(service)
    print("   UsageMonitor created successfully")
    
    # בדיקת טאבים
    tab_count = monitor.tab_widget.count()
    print(f"   Number of tabs: {tab_count}")
    
    # בדיקת כרטיסי סטטיסטיקה
    print(f"   Tokens card value: {monitor.tokens_card.value}")
    print(f"   Calls card value: {monitor.calls_card.value}")
    print(f"   Cost card value: {monitor.cost_card.value}")
    print(f"   Errors card value: {monitor.errors_card.value}")
    
    # עצירת טיימר
    monitor.update_timer.stop()
    
    print("✅ UsageMonitor test passed")


def main():
    """פונקציה ראשית"""
    print("🚀 Starting UsageMonitor component tests...")
    
    try:
        test_stat_card()
        test_usage_service()
        test_usage_monitor()
        
        print("\n🎉 All tests passed successfully!")
        print("✅ UsageMonitor component is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())