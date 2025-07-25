"""
מוניטור שימוש ב-LLM - גרסה פשוטה
מציג סטטיסטיקות שימוש בסיסיות
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, QDateEdit, QPushButton,
    QGroupBox, QGridLayout, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate
from PyQt6.QtGui import QColor

# הוספת נתיב למודלים ושירותים
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from models.llm_models import UsageRecord
from services.usage_service import UsageService


class StatCard(QFrame):
    """כרטיס סטטיסטיקה פשוט"""
    
    def __init__(self, title: str, value: str, icon: str, color: str = "#4CAF50", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedSize(180, 120)
        
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # אייקון
        self.icon_label = QLabel(self.icon)
        self.icon_label.setStyleSheet("font-size: 24px;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # כותרת
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 11px; color: #888888; font-weight: bold;")
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # ערך ראשי
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.color};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # שינוי מהתקופה הקודמת
        self.change_label = QLabel()
        self.change_label.setStyleSheet("font-size: 10px; color: #666666;")
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.change_label.setVisible(False)
        layout.addWidget(self.change_label)
    
    def update_value(self, value: str, change: str = None):
        """עדכון ערך הכרטיס"""
        self.value = value
        self.value_label.setText(value)
        
        if change:
            self.change_label.setText(change)
            self.change_label.setVisible(True)
    
    def apply_styling(self):
        """החלת עיצוב"""
        self.setStyleSheet(f"""
            StatCard {{
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
            }}
            StatCard:hover {{
                border-color: {self.color};
                background-color: #252525;
            }}
            QLabel {{
                background-color: transparent;
                color: #ffffff;
            }}
        """)


class UsageHistoryTable(QTableWidget):
    """טבלת היסטוריית שימוש פשוטה"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.usage_records = []
        
        self.setup_table()
        self.apply_styling()
    
    def setup_table(self):
        """הגדרת הטבלה"""
        # עמודות
        columns = ["תאריך", "מודל", "ספק", "טוקנים", "עלות", "זמן תגובה", "סטטוס"]
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # הגדרות כלליות
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        
        # רוחב עמודות
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # תאריך
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # מודל
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # ספק
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # טוקנים
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # עלות
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # זמן תגובה
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # סטטוס
    
    def load_usage_records(self, records: List[UsageRecord]):
        """טעינת רשומות שימוש"""
        self.usage_records = records
        self.setRowCount(len(records))
        
        for row, record in enumerate(records):
            # תאריך
            date_item = QTableWidgetItem(record.timestamp_formatted)
            self.setItem(row, 0, date_item)
            
            # מודל
            model_item = QTableWidgetItem(record.model_id)
            self.setItem(row, 1, model_item)
            
            # ספק
            provider_item = QTableWidgetItem(record.provider)
            self.setItem(row, 2, provider_item)
            
            # טוקנים
            tokens_item = QTableWidgetItem(f"{record.tokens_used:,}")
            self.setItem(row, 3, tokens_item)
            
            # עלות
            cost_item = QTableWidgetItem(record.cost_formatted)
            self.setItem(row, 4, cost_item)
            
            # זמן תגובה
            time_item = QTableWidgetItem(record.response_time_formatted)
            self.setItem(row, 5, time_item)
            
            # סטטוס
            status_item = QTableWidgetItem(record.status_display)
            
            # צבע לפי סטטוס
            if record.success:
                status_item.setForeground(QColor("#4CAF50"))
            else:
                status_item.setForeground(QColor("#F44336"))
            
            self.setItem(row, 6, status_item)
    
    def apply_styling(self):
        """החלת עיצוב"""
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                color: #ffffff;
                gridline-color: #333;
                border: 1px solid #333;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #333;
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #3d3d3d;
            }
        """)


class UsageMonitor(QWidget):
    """מוניטור שימוש ב-LLM פשוט"""
    
    # אותות
    usage_limit_warning = pyqtSignal(str, float, float)  # limit_type, current, limit
    usage_limit_exceeded = pyqtSignal(str, float, float)  # limit_type, current, limit
    
    def __init__(self, usage_service: UsageService = None, parent=None):
        super().__init__(parent)
        
        # שירותים
        self.usage_service = usage_service or UsageService()
        
        # נתונים
        self.usage_records = []
        
        # טיימר לעדכון אוטומטי
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(30000)  # עדכון כל 30 שניות
        
        # הגדרת ממשק המשתמש
        self.setup_ui()
        self.setup_connections()
        
        # טעינת נתונים ראשונית
        self.refresh_data()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # כותרת
        title = QLabel("מוניטור שימוש LLM")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # כרטיסי סטטיסטיקה
        stats_layout = QHBoxLayout()
        
        self.tokens_card = StatCard("טוקנים בשימוש", "0", "📊", "#2196F3")
        self.calls_card = StatCard("קריאות API", "0", "📞", "#FF9800")
        self.cost_card = StatCard("עלות משוערת", "$0.00", "💰", "#4CAF50")
        self.errors_card = StatCard("שגיאות", "0", "⚠️", "#F44336")
        
        stats_layout.addWidget(self.tokens_card)
        stats_layout.addWidget(self.calls_card)
        stats_layout.addWidget(self.cost_card)
        stats_layout.addWidget(self.errors_card)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # סטטיסטיקות מפורטות
        details_group = QGroupBox("פירוט נוסף")
        details_layout = QGridLayout(details_group)
        
        # ממוצע זמן תגובה
        details_layout.addWidget(QLabel("ממוצע זמן תגובה:"), 0, 0)
        self.avg_response_time_label = QLabel("0.0s")
        self.avg_response_time_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        details_layout.addWidget(self.avg_response_time_label, 0, 1)
        
        # אחוז הצלחה
        details_layout.addWidget(QLabel("אחוז הצלחה:"), 0, 2)
        self.success_rate_label = QLabel("0%")
        self.success_rate_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        details_layout.addWidget(self.success_rate_label, 0, 3)
        
        # ספקים פעילים
        details_layout.addWidget(QLabel("ספקים פעילים:"), 1, 0)
        self.active_providers_label = QLabel("0")
        self.active_providers_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        details_layout.addWidget(self.active_providers_label, 1, 1)
        
        # מודלים בשימוש
        details_layout.addWidget(QLabel("מודלים בשימוש:"), 1, 2)
        self.active_models_label = QLabel("0")
        self.active_models_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        details_layout.addWidget(self.active_models_label, 1, 3)
        
        layout.addWidget(details_group)
        
        # טבלת היסטוריה
        history_group = QGroupBox("היסטוריית שימוש")
        history_layout = QVBoxLayout(history_group)
        
        self.history_table = UsageHistoryTable()
        history_layout.addWidget(self.history_table)
        
        layout.addWidget(history_group)
        
        # כפתור רענון
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        
        refresh_button = QPushButton("🔄 רענון נתונים")
        refresh_button.clicked.connect(self.refresh_data)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        refresh_layout.addWidget(refresh_button)
        
        layout.addLayout(refresh_layout)
        
        # עיצוב קבוצות
        for group in [details_group, history_group]:
            group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #555;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
    
    def setup_connections(self):
        """הגדרת חיבורים לאותות"""
        # חיבור לאותות שירות השימוש
        self.usage_service.usage_recorded.connect(self.on_usage_recorded)
        self.usage_service.usage_limit_reached.connect(self.on_limit_reached)
        self.usage_service.usage_warning.connect(self.on_usage_warning)
    
    def refresh_data(self):
        """רענון כל הנתונים"""
        try:
            # עדכון סטטיסטיקות כלליות
            self.update_overview_stats()
            
            # עדכון היסטוריה
            self.update_history_data()
        
        except Exception as e:
            print(f"שגיאה ברענון נתונים: {e}")
    
    def update_overview_stats(self):
        """עדכון סטטיסטיקות סקירה כללית"""
        try:
            # סטטיסטיקות יומיות
            today = datetime.now().date()
            daily_stats = self.usage_service.get_usage_summary(
                start_date=today,
                end_date=today
            )
            
            # סטטיסטיקות חודשיות
            month_start = datetime.now().replace(day=1).date()
            monthly_stats = self.usage_service.get_usage_summary(
                start_date=month_start,
                end_date=today
            )
            
            # עדכון כרטיסי סטטיסטיקה
            self.tokens_card.update_value(
                f"{monthly_stats['total_tokens']:,}",
                f"+{daily_stats['total_tokens']:,} היום"
            )
            
            self.calls_card.update_value(
                f"{monthly_stats['total_requests']:,}",
                f"+{daily_stats['total_requests']:,} היום"
            )
            
            self.cost_card.update_value(
                f"${monthly_stats['total_cost']:.2f}",
                f"+${daily_stats['total_cost']:.2f} היום"
            )
            
            # חישוב שגיאות
            error_count = monthly_stats['total_requests'] - (monthly_stats['total_requests'] * monthly_stats['success_rate'])
            daily_error_count = daily_stats['total_requests'] - (daily_stats['total_requests'] * daily_stats['success_rate'])
            
            self.errors_card.update_value(
                f"{int(error_count)}",
                f"+{int(daily_error_count)} היום"
            )
            
            # עדכון פרטים נוספים
            self.avg_response_time_label.setText(f"{monthly_stats['avg_response_time']:.2f}s")
            self.success_rate_label.setText(f"{monthly_stats['success_rate']*100:.1f}%")
            self.active_providers_label.setText(f"{monthly_stats['unique_providers']}")
            self.active_models_label.setText(f"{monthly_stats['unique_models']}")
        
        except Exception as e:
            print(f"שגיאה בעדכון סטטיסטיקות: {e}")
    
    def update_history_data(self):
        """עדכון נתוני היסטוריה"""
        try:
            # טעינת רשומות אחרונות
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            self.usage_records = self.usage_service.get_usage_records(
                start_date=start_date,
                end_date=end_date,
                limit=100
            )
            
            # עדכון הטבלה
            self.history_table.load_usage_records(self.usage_records)
        
        except Exception as e:
            print(f"שגיאה בעדכון היסטוריה: {e}")
    
    def on_usage_recorded(self, usage_record: UsageRecord):
        """טיפול ברישום שימוש חדש"""
        # עדכון נתונים בזמן אמת
        QTimer.singleShot(1000, self.update_overview_stats)
    
    def on_limit_reached(self, limit_type: str, current_value: float):
        """טיפול בחריגה ממגבלה"""
        self.usage_limit_exceeded.emit(limit_type, current_value, 0)
        print(f"⚠️ חריגה ממגבלה: {limit_type} - {current_value}")
    
    def on_usage_warning(self, limit_type: str, current_value: float, limit_value: float):
        """טיפול באזהרת מגבלה"""
        self.usage_limit_warning.emit(limit_type, current_value, limit_value)
        print(f"🟡 אזהרת מגבלה: {limit_type} - {current_value}/{limit_value}")