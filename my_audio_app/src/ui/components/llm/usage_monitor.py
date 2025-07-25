"""
מוניטור שימוש ב-LLM
מציג סטטיסטיקות שימוש, גרפים, היסטוריה ומעקב אחר מגבלות
"""

import os
import sys
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, QDateEdit, QPushButton,
    QGroupBox, QGridLayout, QProgressBar, QMessageBox, QTabWidget,
    QScrollArea, QSizePolicy, QSpacerItem, QCheckBox, QSpinBox,
    QDoubleSpinBox, QSlider, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QDate, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush

# הוספת נתיב למודלים ושירותים
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from models.llm_models import UsageRecord
from services.usage_service import UsageService


class StatCard(QFrame):
    """כרטיס סטטיסטיקה"""
    
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
        
        # כותרת עם אייקון
        header_layout = QHBoxLayout()
        
        self.icon_label = QLabel(self.icon)
        self.icon_label.setStyleSheet("font-size: 24px;")
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 11px; color: #888888; font-weight: bold;")
        self.title_label.setWordWrap(True)
        
        header_layout.addWidget(self.icon_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(self.title_label)
        
        # ערך ראשי
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.color};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # שינוי מהתקופה הקודמת (אופציונלי)
        self.change_label = QLabel()
        self.change_label.setStyleSheet("font-size: 10px; color: #666666;")
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.change_label.setVisible(False)
        layout.addWidget(self.change_label)
        
        layout.addStretch()
    
    def update_value(self, value: str, change: str = None):
        """עדכון ערך הכרטיס"""
        self.value = value
        self.value_label.setText(value)
        
        if change:
            self.change_label.setText(change)
            self.change_label.setVisible(True)
            
            # צבע לפי כיוון השינוי
            if change.startswith("+"):
                self.change_label.setStyleSheet("font-size: 10px; color: #F44336;")  # אדום לעלייה בעלות
            elif change.startswith("-"):
                self.change_label.setStyleSheet("font-size: 10px; color: #4CAF50;")  # ירוק לירידה בעלות
            else:
                self.change_label.setStyleSheet("font-size: 10px; color: #666666;")
    
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


class SimpleChart(QWidget):
    """גרף פשוט לתצוגת נתונים"""
    
    def __init__(self, title: str, data: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.title = title
        self.data = data
        self.setMinimumSize(300, 200)
        
        self.setup_ui()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # כותרת
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # אזור הגרף
        self.chart_area = QLabel("📈 Chart Placeholder")
        self.chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_area.setStyleSheet("""
            background-color: #2d2d2d;
            border: 1px solid #444;
            border-radius: 4px;
            color: #888888;
            font-size: 12px;
        """)
        self.chart_area.setMinimumHeight(150)
        layout.addWidget(self.chart_area)
        
        # מידע נוסף על הנתונים
        if self.data:
            info_text = f"נתונים: {len(self.data)} נקודות"
            if self.data:
                latest = self.data[-1] if self.data else {}
                if 'date' in latest:
                    info_text += f" | אחרון: {latest['date']}"
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("font-size: 10px; color: #666666; margin-top: 5px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)
    
    def update_data(self, data: List[Dict[str, Any]]):
        """עדכון נתוני הגרף"""
        self.data = data
        # כאן יהיה עדכון הגרף האמיתי
        info_text = f"נתונים עודכנו: {len(data)} נקודות"
        if data:
            latest = data[-1]
            if 'date' in latest:
                info_text += f" | אחרון: {latest['date']}"
        
        self.chart_area.setText(f"📈 {info_text}")


class UsageMonitor(QWidget):
    """מוניטור שימוש ב-LLM עם סטטיסטיקות, גרפים והיסטוריה"""
    
    # אותות
    usage_limit_warning = pyqtSignal(str, float, float)  # limit_type, current, limit
    usage_limit_exceeded = pyqtSignal(str, float, float)  # limit_type, current, limit
    
    def __init__(self, usage_service: UsageService = None, parent=None):
        super().__init__(parent)
        
        # שירותים
        self.usage_service = usage_service or UsageService()
        
        # נתונים
        self.current_stats = {}
        self.usage_trends = []
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
        
        # טאבים
        self.tab_widget = QTabWidget()
        
        # טאב סקירה כללית
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 סקירה כללית")
        
        # טאב היסטוריה
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📋 היסטוריה")
        
        # טאב מגבלות
        self.limits_tab = self.create_limits_tab()
        self.tab_widget.addTab(self.limits_tab, "⚠️ מגבלות")
        
        layout.addWidget(self.tab_widget)
        
        # עיצוב טאבים
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
        """)
    
    def create_overview_tab(self) -> QWidget:
        """יצירת טאב סקירה כללית"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
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
        
        # גרפים
        charts_layout = QHBoxLayout()
        
        # גרף שימוש לאורך זמן
        self.usage_chart = SimpleChart("שימוש לאורך זמן", [])
        charts_layout.addWidget(self.usage_chart)
        
        # גרף התפלגות ספקים
        self.providers_chart = SimpleChart("התפלגות ספקים", [])
        charts_layout.addWidget(self.providers_chart)
        
        layout.addLayout(charts_layout)
        
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
        
        # עיצוב
        details_group.setStyleSheet("""
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
        
        return widget
    
    def create_history_tab(self) -> QWidget:
        """יצירת טאב היסטוריה - placeholder"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # פילטרים בסיסיים
        filters_group = QGroupBox("פילטרים")
        filters_layout = QHBoxLayout(filters_group)
        
        # טווח תאריכים
        filters_layout.addWidget(QLabel("מתאריך:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        filters_layout.addWidget(self.date_from)
        
        filters_layout.addWidget(QLabel("עד תאריך:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filters_layout.addWidget(self.date_to)
        
        # ספק
        filters_layout.addWidget(QLabel("ספק:"))
        self.provider_filter = QComboBox()
        self.provider_filter.addItem("כל הספקים")
        filters_layout.addWidget(self.provider_filter)
        
        # מודל
        filters_layout.addWidget(QLabel("מודל:"))
        self.model_filter = QComboBox()
        self.model_filter.addItem("כל המודלים")
        filters_layout.addWidget(self.model_filter)
        
        # סטטוס
        filters_layout.addWidget(QLabel("סטטוס:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["הכל", "הצליח", "נכשל"])
        filters_layout.addWidget(self.status_filter)
        
        filters_layout.addStretch()
        
        layout.addWidget(filters_group)
        
        # טבלת היסטוריה פשוטה
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "תאריך", "מודל", "ספק", "טוקנים", "עלות", "זמן תגובה", "סטטוס"
        ])
        layout.addWidget(self.history_table)
        
        # עיצוב פילטרים
        filters_group.setStyleSheet("""
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
            QDateEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
            }
        """)
        
        return widget
    
    def create_limits_tab(self) -> QWidget:
        """יצירת טאב מגבלות - placeholder"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # מגבלות בסיסיות
        limits_group = QGroupBox("מגבלות שימוש")
        limits_layout = QGridLayout(limits_group)
        
        # עלות יומית
        limits_layout.addWidget(QLabel("עלות יומית מקסימלית:"), 0, 0)
        self.daily_cost_spin = QDoubleSpinBox()
        self.daily_cost_spin.setRange(0, 1000)
        self.daily_cost_spin.setValue(10.0)
        self.daily_cost_spin.setSuffix(" $")
        limits_layout.addWidget(self.daily_cost_spin, 0, 1)
        
        # עלות חודשית
        limits_layout.addWidget(QLabel("עלות חודשית מקסימלית:"), 1, 0)
        self.monthly_cost_spin = QDoubleSpinBox()
        self.monthly_cost_spin.setRange(0, 10000)
        self.monthly_cost_spin.setValue(100.0)
        self.monthly_cost_spin.setSuffix(" $")
        limits_layout.addWidget(self.monthly_cost_spin, 1, 1)
        
        layout.addWidget(limits_group)
        
        # התראות
        alerts_group = QGroupBox("התראות פעילות")
        alerts_layout = QVBoxLayout(alerts_group)
        
        self.alerts_text = QTextEdit()
        self.alerts_text.setMaximumHeight(150)
        self.alerts_text.setReadOnly(True)
        self.alerts_text.setPlaceholderText("אין התראות פעילות")
        self.alerts_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ffffff;
                font-family: monospace;
            }
        """)
        alerts_layout.addWidget(self.alerts_text)
        
        layout.addWidget(alerts_group)
        layout.addStretch()
        
        # עיצוב
        for group in [limits_group, alerts_group]:
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
                QDoubleSpinBox {
                    background-color: #2d2d2d;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 4px;
                    color: #ffffff;
                }
            """)
        
        return widget
    
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
            
            # בדיקת מגבלות
            self.check_current_limits()
        
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
            
            # עדכון גרפים
            trends = self.usage_service.get_usage_trends(30)
            self.usage_chart.update_data(trends)
            
            provider_stats = self.usage_service.get_usage_by_provider(month_start, today)
            provider_data = [{"name": k, "value": v["total_cost"]} for k, v in provider_stats.items()]
            self.providers_chart.update_data(provider_data)
        
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
            self.history_table.setRowCount(len(self.usage_records))
            
            for row, record in enumerate(self.usage_records):
                self.history_table.setItem(row, 0, QTableWidgetItem(record.timestamp_formatted))
                self.history_table.setItem(row, 1, QTableWidgetItem(record.model_id))
                self.history_table.setItem(row, 2, QTableWidgetItem(record.provider))
                self.history_table.setItem(row, 3, QTableWidgetItem(f"{record.tokens_used:,}"))
                self.history_table.setItem(row, 4, QTableWidgetItem(record.cost_formatted))
                self.history_table.setItem(row, 5, QTableWidgetItem(record.response_time_formatted))
                self.history_table.setItem(row, 6, QTableWidgetItem(record.status_display))
        
        except Exception as e:
            print(f"שגיאה בעדכון היסטוריה: {e}")
    
    def check_current_limits(self):
        """בדיקת מגבלות נוכחיות"""
        try:
            now = datetime.now()
            alerts = []
            
            # בדיקת מגבלות יומיות
            today = now.date()
            daily_stats = self.usage_service.get_usage_summary(today, today)
            
            daily_cost_limit = self.usage_service.get_usage_limit("daily_cost")
            if daily_cost_limit and daily_cost_limit["is_enabled"]:
                current_cost = daily_stats["total_cost"]
                limit_value = daily_cost_limit["limit_value"]
                
                if current_cost >= limit_value:
                    alerts.append(f"⚠️ חריגה ממגבלת עלות יומית: ${current_cost:.2f} / ${limit_value:.2f}")
                elif current_cost >= limit_value * 0.8:
                    alerts.append(f"🟡 התקרבות למגבלת עלות יומית: ${current_cost:.2f} / ${limit_value:.2f}")
            
            # עדכון תצוגת התראות
            if alerts:
                self.alerts_text.setPlainText("\n".join(alerts))
            else:
                self.alerts_text.setPlainText("✅ כל המגבלות תקינות")
        
        except Exception as e:
            print(f"שגיאה בבדיקת מגבלות: {e}")
    
    def on_usage_recorded(self, usage_record: UsageRecord):
        """טיפול ברישום שימוש חדש"""
        # עדכון נתונים בזמן אמת
        QTimer.singleShot(1000, self.update_overview_stats)
    
    def on_limit_reached(self, limit_type: str, current_value: float):
        """טיפול בחריגה ממגבלה"""
        self.usage_limit_exceeded.emit(limit_type, current_value, 0)
        
        # הודעת התראה
        limit_names = {
            "daily_cost": "עלות יומית",
            "monthly_cost": "עלות חודשית", 
            "daily_tokens": "טוקנים יומיים",
            "monthly_tokens": "טוקנים חודשיים",
            "hourly_requests": "בקשות שעתיות"
        }
        
        limit_name = limit_names.get(limit_type, limit_type)
        
        QMessageBox.warning(
            self, "חריגה ממגבלה",
            f"חרגת ממגבלת {limit_name}!\n\nערך נוכחי: {current_value}"
        )
        
        # עדכון התראות
        self.check_current_limits()
    
    def on_usage_warning(self, limit_type: str, current_value: float, limit_value: float):
        """טיפול באזהרת מגבלה"""
        self.usage_limit_warning.emit(limit_type, current_value, limit_value)

        # עדכון התראות
        self.check_current_limits()

    def export_history(self) -> None:
        """ייצוא היסטוריית שימוש לקובץ CSV"""
        if not self.usage_records:
            QMessageBox.information(self, "ייצוא היסטוריה", "אין רשומות לייצוא")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "בחר מיקום לשמירת הייצוא",
            "usage_history.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                headers = [
                    "id",
                    "timestamp",
                    "model_id",
                    "provider",
                    "tokens_used",
                    "cost",
                    "response_time",
                    "success"
                ]
                f.write(",".join(headers) + "\n")
                for record in self.usage_records:
                    row = [
                        record.id,
                        record.timestamp.isoformat(),
                        record.model_id,
                        record.provider,
                        str(record.tokens_used),
                        str(record.cost),
                        str(record.response_time),
                        str(record.success)
                    ]
                    f.write(",".join(row) + "\n")

            QMessageBox.information(self, "ייצוא היסטוריה", "הייצוא הושלם בהצלחה")
        except Exception as e:
            QMessageBox.warning(self, "שגיאה בייצוא", str(e))

