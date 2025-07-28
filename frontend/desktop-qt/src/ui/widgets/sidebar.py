from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class Sidebar(QWidget):
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setObjectName("sidebar")
        
        # Add shadow effect to sidebar
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(5, 0)
        self.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(16, 24, 16, 24)
        self.layout.setSpacing(8)

        self.buttons = {}
        
        # Add logo/title section
        self._add_logo_section()

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
        
        # Add footer section
        self._add_footer_section()
    
    def _add_logo_section(self):
        """Add logo and app title section"""
        logo_section = QVBoxLayout()
        logo_section.setSpacing(8)
        
        # App title
        app_title = QLabel("🎵 Audio Chat Studio")
        app_title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title.setStyleSheet("""
            QLabel {
                color: #3b82f6;
                padding: 16px 12px;
                background-color: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
                margin-bottom: 8px;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        logo_section.addWidget(app_title)
        
        # Version label
        version_label = QLabel("v1.0.0")
        version_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            color: #71717a; 
            margin-bottom: 20px;
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        """)
        logo_section.addWidget(version_label)
        
        self.layout.addLayout(logo_section)
    
    def _add_footer_section(self):
        """Add footer section with status"""
        footer_section = QVBoxLayout()
        footer_section.setSpacing(8)
        
        # Status indicator
        status_label = QLabel("🟢 Ready")
        status_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("""
            QLabel {
                color: #22c55e;
                padding: 8px 12px;
                background-color: rgba(34, 197, 94, 0.1);
                border: 1px solid rgba(34, 197, 94, 0.2);
                border-radius: 6px;
                margin-top: 12px;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        footer_section.addWidget(status_label)
        
        self.layout.addLayout(footer_section)

    def _add_section(self, title, items):
        # Section header with shadcn styling
        section_label = QLabel(title.upper())
        section_label.setFont(QFont("Inter", 11, QFont.Weight.DemiBold))
        section_label.setStyleSheet("""
            QLabel {
                color: #71717a;
                margin-top: 24px;
                margin-bottom: 8px;
                margin-left: 8px;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                letter-spacing: 0.5px;
            }
        """)
        self.layout.addWidget(section_label)

        for text, page in items:
            self._add_button(text, page)

    def _add_button(self, text, page_name):
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.clicked.connect(lambda: self.page_changed.emit(page_name))
        
        # shadcn button styling
        button.setFont(QFont("Inter", 14, QFont.Weight.Medium))
        button.setMinimumHeight(40)
        
        # Add subtle shadow to buttons
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        button.setGraphicsEffect(shadow)
        
        self.layout.addWidget(button)
        self.buttons[page_name] = button

    def set_active_page(self, page_name):
        if page_name in self.buttons:
            self.buttons[page_name].setChecked(True)
