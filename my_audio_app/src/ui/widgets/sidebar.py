from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class Sidebar(QWidget):
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setObjectName("sidebar")
        
        # הגדרת סגנון רקע לסיידבר
        self.setStyleSheet("""
            QWidget#sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(10, 20, 10, 20)
        self.layout.setSpacing(10)

        self.buttons = {}

        # Sections
        self._add_section("Core Workflow", [
            ("🏠 Home", "home"),
            ("⚡ AI Audio Actions", "audio_actions"),
            ("📤 Audio Exports", "exports"),
            ("📊 File Stats", "file_stats"),
        ])

        self._add_section("Advanced", [
            ("🧠 AI Terminal", "terminal"),
            ("🧬 LLM Management", "llm_management"),
        ])

        self._add_section("System", [
            ("🔐 Auth Settings", "auth"),
            ("👤 Profile", "profile"),
            ("🗄️ Data Management", "data_management"),
        ])

        self.layout.addStretch()

    def _add_section(self, title, items):
        section_label = QLabel(title)
        section_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: white; opacity: 0.8;")
        self.layout.addWidget(section_label)

        for text, page in items:
            self._add_button(text, page)

    def _add_button(self, text, page_name):
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.clicked.connect(lambda: self.page_changed.emit(page_name))
        
        # עיצוב כפתור עם טקסט לבן
        button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: normal;
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
            QPushButton:hover:!checked {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        self.layout.addWidget(button)
        self.buttons[page_name] = button

    def set_active_page(self, page_name):
        if page_name in self.buttons:
            self.buttons[page_name].setChecked(True)
