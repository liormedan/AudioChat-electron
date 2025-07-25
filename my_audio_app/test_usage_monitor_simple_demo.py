#!/usr/bin/env python3
"""
דמו פשוט לרכיב UsageMonitor
מציג את רכיב מוניטור השימוש עם נתונים דמה
"""

import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
import uuid

# הוספת נתיב למודלים
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.llm_models import UsageRecord
from services.usage_service import UsageService
from ui.components.llm.usage_monitor_simple import UsageMonitor


class UsageMonitorSimpleDemo(QMainWindow):
    """חלון דמו למוניטור שימוש פשוט"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Usage Monitor Simple Demo - מוניטור שימוש LLM פשוט")
        self.setGeometry(100, 100, 1000, 700)
        
        # יצירת שירות שימוש
        self.usage_service = UsageService()
        
        # יצירת נתונים דמה
        self.create_sample_data()
        
        # יצירת הממשק
        self.setup_ui()
        
        # טיימר להוספת נתונים חדשים
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.add_random_usage)
        self.data_timer.start(3000)  # כל 3 שניות
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # יצירת רכיב מוניטור השימוש
        self.usage_monitor = UsageMonitor(self.usage_service)
        layout.addWidget(self.usage_monitor)
        
        # חיבור לאותות
        self.usage_monitor.usage_limit_warning.connect(self.on_usage_warning)
        self.usage_monitor.usage_limit_exceeded.connect(self.on_usage_exceeded)
    
    def create_sample_data(self):
        """יצירת נתונים דמה"""
        providers = ["OpenAI", "Anthropic", "Google"]
        models = {
            "OpenAI": ["gpt-4", "gpt-3.5-turbo"],
            "Anthropic": ["claude-3-opus", "claude-3-sonnet"],
            "Google": ["gemini-pro"]
        }
        
        # יצירת רשומות לשבועיים האחרונים
        now = datetime.now()
        
        for i in range(50):  # 50 רשומות
            # בחירת ספק ומודל אקראיים
            import random
            provider = random.choice(providers)
            model = random.choice(models[provider])
            
            # יצירת זמן אקראי בשבועיים האחרונים
            days_ago = random.randint(0, 14)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # יצירת נתונים אקראיים
            tokens_used = random.randint(100, 3000)
            cost_per_token = random.uniform(0.00001, 0.00003)
            cost = tokens_used * cost_per_token
            response_time = random.uniform(0.5, 2.5)
            success = random.random() > 0.1  # 90% הצלחה
            
            # יצירת רשומת שימוש
            record = UsageRecord(
                id=str(uuid.uuid4()),
                timestamp=timestamp,
                model_id=model,
                provider=provider,
                tokens_used=tokens_used,
                cost=cost,
                response_time=response_time,
                success=success,
                error_message="Connection timeout" if not success else None,
                request_type="chat",
                user_id="demo_user",
                session_id=str(uuid.uuid4())[:8]
            )
            
            # רישום השימוש
            self.usage_service.record_usage(record)
        
        print(f"נוצרו {50} רשומות שימוש דמה")
    
    def add_random_usage(self):
        """הוספת רשומת שימוש אקראית"""
        import random
        
        providers = ["OpenAI", "Anthropic", "Google"]
        models = {
            "OpenAI": ["gpt-4", "gpt-3.5-turbo"],
            "Anthropic": ["claude-3-opus", "claude-3-sonnet"],
            "Google": ["gemini-pro"]
        }
        
        provider = random.choice(providers)
        model = random.choice(models[provider])
        
        tokens_used = random.randint(100, 1500)
        cost_per_token = random.uniform(0.00001, 0.00003)
        cost = tokens_used * cost_per_token
        response_time = random.uniform(0.5, 2.0)
        success = random.random() > 0.15  # 85% הצלחה
        
        record = UsageRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            model_id=model,
            provider=provider,
            tokens_used=tokens_used,
            cost=cost,
            response_time=response_time,
            success=success,
            error_message="Rate limit exceeded" if not success else None,
            request_type="chat",
            user_id="demo_user",
            session_id=str(uuid.uuid4())[:8]
        )
        
        self.usage_service.record_usage(record)
        print(f"נוספה רשומת שימוש חדשה: {provider} - {model} - {tokens_used} tokens")
    
    def on_usage_warning(self, limit_type: str, current: float, limit: float):
        """טיפול באזהרת מגבלה"""
        print(f"⚠️ אזהרת מגבלה: {limit_type} - {current:.2f} / {limit:.2f}")
    
    def on_usage_exceeded(self, limit_type: str, current: float, limit: float):
        """טיפול בחריגה ממגבלה"""
        print(f"🚨 חריגה ממגבלה: {limit_type} - {current:.2f} / {limit:.2f}")
    
    def closeEvent(self, event):
        """טיפול בסגירת החלון"""
        self.data_timer.stop()
        if hasattr(self, 'usage_monitor'):
            self.usage_monitor.update_timer.stop()
        event.accept()


def main():
    """פונקציה ראשית"""
    app = QApplication(sys.argv)
    
    # הגדרת עיצוב כהה
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
    """)
    
    # יצירת והצגת החלון
    demo = UsageMonitorSimpleDemo()
    demo.show()
    
    print("🚀 דמו מוניטור שימוש LLM פשוט הופעל")
    print("📊 הרכיב מציג סטטיסטיקות שימוש והיסטוריה")
    print("🔄 נתונים חדשים נוספים כל 3 שניות")
    print("❌ לסגירה: Ctrl+C או סגירת החלון")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
