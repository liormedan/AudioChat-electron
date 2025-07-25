from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
)
from PyQt6.QtCore import Qt

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    FigureCanvas = None  # type: ignore
    Figure = None  # type: ignore
    MATPLOTLIB_AVAILABLE = False

from services.file_stats_data_manager import FileStatsDataManager


class FileStatsPage(QWidget):
    def __init__(self, data_manager: FileStatsDataManager = None):
        super().__init__()
        self.data_manager = data_manager or FileStatsDataManager()
        self.setObjectName("fileStatsPage")

        self.pie_canvas = None
        self.pie_ax = None
        self.bar_canvas = None
        self.bar_ax = None
        
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
            timeline = self.data_manager.get_upload_timeline()

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

            self._update_pie_chart(formats)
            self._update_bar_chart(timeline)
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

        if MATPLOTLIB_AVAILABLE:
            self.pie_canvas = FigureCanvas(Figure(figsize=(3, 3)))
            self.pie_ax = self.pie_canvas.figure.subplots()
            self.pie_canvas.figure.tight_layout()
            self.pie_canvas.figure.set_facecolor("#1e1e1e")
            layout.addWidget(self.pie_canvas)
        else:
            placeholder = QLabel("matplotlib not available")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setMinimumHeight(150)
            placeholder.setStyleSheet("color: white;")
            layout.addWidget(placeholder)
            self.pie_canvas = None
            self.pie_ax = None

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

        if MATPLOTLIB_AVAILABLE:
            self.bar_canvas = FigureCanvas(Figure(figsize=(3, 3)))
            self.bar_ax = self.bar_canvas.figure.subplots()
            self.bar_canvas.figure.tight_layout()
            self.bar_canvas.figure.set_facecolor("#1e1e1e")
            layout.addWidget(self.bar_canvas)
        else:
            placeholder = QLabel("matplotlib not available")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setMinimumHeight(150)
            placeholder.setStyleSheet("color: white;")
            layout.addWidget(placeholder)
            self.bar_canvas = None
            self.bar_ax = None

        return chart_box

    def _update_pie_chart(self, formats):
        if not MATPLOTLIB_AVAILABLE or self.pie_ax is None:
            return
        self.pie_ax.clear()
        if not formats:
            self.pie_ax.text(
                0.5,
                0.5,
                "No Data",
                ha="center",
                va="center",
                color="white",
            )
            self.pie_ax.set_xticks([])
            self.pie_ax.set_yticks([])
        else:
            labels = list(formats.keys())
            values = list(formats.values())
            self.pie_ax.pie(values, labels=labels, autopct="%1.0f%%")
        self.pie_canvas.draw()

    def _update_bar_chart(self, timeline):
        if not MATPLOTLIB_AVAILABLE or self.bar_ax is None:
            return
        self.bar_ax.clear()
        if not timeline:
            self.bar_ax.text(
                0.5,
                0.5,
                "No Data",
                ha="center",
                va="center",
                color="white",
            )
            self.bar_ax.set_xticks([])
            self.bar_ax.set_yticks([])
        else:
            dates = list(timeline.keys())
            counts = list(timeline.values())
            self.bar_ax.bar(dates, counts, color="#2196F3")
            self.bar_ax.set_xticklabels(dates, rotation=45, ha="right")
        self.bar_canvas.draw()
    
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

