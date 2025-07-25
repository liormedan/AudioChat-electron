from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor

from services.file_stats_data_manager import FileStatsDataManager


class FileStatsPage(QWidget):
    def __init__(self, data_manager: FileStatsDataManager = None):
        super().__init__()
        self.data_manager = data_manager or FileStatsDataManager()
        self.setObjectName("fileStatsPage")
        
        # סגנון כללי לדף - רקע שחור וטקסט לבן
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
            }
            QGroupBox {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #333;
            }
            QGroupBox::title {
                color: white;
            }
            QTableWidget {
                background-color: #1e1e1e;
                color: white;
                gridline-color: #333;
                border: 1px solid #333;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
                border: 1px solid #444;
            }
            QTableWidget::item {
                border-bottom: 1px solid #333;
            }
        """)
        
        # יצירת הלייאאוט הראשי
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # כותרת הדף
        title = QLabel("📊 File Statistics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px; color: white;")
        main_layout.addWidget(title)
        
        # יצירת שורת סיכום עם מספרים
        summary_layout = QHBoxLayout()
        
        # קופסאות סטטיסטיקה
        self.total_files_label = self._add_stat_box(summary_layout, "Total Files", "0", "🗂️")
        self.total_duration_label = self._add_stat_box(summary_layout, "Total Duration", "0:00", "⏱️")
        self.formats_label = self._add_stat_box(summary_layout, "Formats", "-", "🔤")
        self.last_upload_label = self._add_stat_box(summary_layout, "Last Upload", "-", "📅")
        
        main_layout.addLayout(summary_layout)
        
        # יצירת שורה עם גרפים
        charts_layout = QHBoxLayout()
        
        # גרף עוגה - סוגי קבצים
        pie_chart = self._create_pie_chart()
        charts_layout.addWidget(pie_chart)
        
        # גרף עמודות - העלאות לפי יום
        bar_chart = self._create_bar_chart()
        charts_layout.addWidget(bar_chart)
        
        main_layout.addLayout(charts_layout)
        
        # טבלת קבצים אחרונים
        main_layout.addWidget(self._create_recent_files_table())

        # מרווח בסוף
        main_layout.addStretch()

        # Load initial data
        self.refresh_data()

    def refresh_data(self):
        """Load statistics from the data manager and update widgets."""
        try:
            total_files = self.data_manager.get_total_files_count()
            total_duration = self.data_manager.get_total_duration()
            formats = self.data_manager.get_format_distribution()
            last_upload = self.data_manager.get_last_upload_date()
            recent_files = self.data_manager.get_recent_files()

            self.total_files_label.setText(str(total_files))

            minutes, sec = divmod(total_duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours:
                duration_str = f"{hours}:{minutes:02d}:{sec:02d}"
            else:
                duration_str = f"{minutes}:{sec:02d}"
            self.total_duration_label.setText(duration_str)

            self.formats_label.setText(
                ", ".join(sorted(formats.keys())) if formats else "-"
            )

            if last_upload:
                self.last_upload_label.setText(
                    last_upload.strftime("%Y-%m-%d %H:%M")
                )
            else:
                self.last_upload_label.setText("-")

            table = self.recent_files_table
            table.setRowCount(len(recent_files))
            for row, info in enumerate(recent_files):
                table.setItem(row, 0, QTableWidgetItem(info.name))
                table.setItem(row, 1, QTableWidgetItem(info.format.upper()))
                table.setItem(row, 2, QTableWidgetItem(info.size_formatted))
                table.setItem(row, 3, QTableWidgetItem(info.duration_formatted))
                table.setItem(
                    row,
                    4,
                    QTableWidgetItem(info.upload_date.strftime("%Y-%m-%d")),
                )
        except Exception as exc:
            print(f"Failed to refresh file statistics: {exc}")
    
    def _add_stat_box(self, layout, title, value, icon):
        """יוצר קופסת סטטיסטיקה עם כותרת, ערך ואייקון"""
        box = QGroupBox()
        box.setStyleSheet("""
            QGroupBox {
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #333;
            }
        """)
        
        box_layout = QVBoxLayout(box)
        
        # אייקון וכותרת
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #aaa; font-size: 14px;")
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        
        box_layout.addLayout(header)
        
        # ערך
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        box_layout.addWidget(value_label)

        layout.addWidget(box)
        return value_label
    
    def _create_pie_chart(self):
        """יוצר גרף עוגה פשוט לסוגי קבצים"""
        chart_box = QGroupBox("File Types")
        chart_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #333;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: #1e1e1e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(chart_box)
        
        # כאן יש להוסיף גרף עוגה אמיתי - לדוגמה נשתמש בתווית
        chart_placeholder = QLabel("Pie Chart: MP3 (60%), WAV (25%), FLAC (15%)")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setMinimumHeight(150)
        chart_placeholder.setStyleSheet("color: white;")
        layout.addWidget(chart_placeholder)
        
        # לגנדה
        legend = QHBoxLayout()
        self._add_legend_item(legend, "MP3", "#2196F3")
        self._add_legend_item(legend, "WAV", "#4CAF50")
        self._add_legend_item(legend, "FLAC", "#FFC107")
        layout.addLayout(legend)
        
        return chart_box
    
    def _create_bar_chart(self):
        """יוצר גרף עמודות פשוט להעלאות לפי יום"""
        chart_box = QGroupBox("Uploads by Day")
        chart_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #333;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: #1e1e1e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(chart_box)
        
        # כאן יש להוסיף גרף עמודות אמיתי - לדוגמה נשתמש בתווית
        chart_placeholder = QLabel("Bar Chart: Mon (5), Tue (8), Wed (12), Thu (7), Fri (15)")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setMinimumHeight(150)
        chart_placeholder.setStyleSheet("color: white;")
        layout.addWidget(chart_placeholder)
        
        return chart_box
    
    def _add_legend_item(self, layout, text, color):
        """מוסיף פריט ללגנדה של הגרף"""
        color_box = QFrame()
        color_box.setFixedSize(12, 12)
        color_box.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        
        layout.addWidget(color_box)
        layout.addWidget(QLabel(text))
        layout.addSpacing(10)
    
    def _create_recent_files_table(self):
        """יוצר טבלה עם הקבצים האחרונים שהועלו"""
        group_box = QGroupBox("Recent Files")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #333;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: #1e1e1e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(group_box)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Filename", "Format", "Size", "Duration", "Upload Date"])
        self.recent_files_table = table
        
        table.setRowCount(0)
        
        table.setColumnWidth(0, 200)  # שם קובץ
        table.setColumnWidth(1, 80)   # פורמט
        table.setColumnWidth(2, 100)  # גודל
        table.setColumnWidth(3, 100)  # משך
        table.setColumnWidth(4, 150)  # תאריך העלאה
        
        layout.addWidget(table)
        
        return group_box

