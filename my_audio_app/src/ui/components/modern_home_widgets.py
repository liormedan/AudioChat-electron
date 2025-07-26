"""
Modern widgets specifically for the home page
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                           QGraphicsDropShadowEffect, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QLinearGradient
from ui.components.shadcn_components import ShadcnCard, ShadcnButton, ShadcnBadge


class StatsCard(ShadcnCard):
    """Statistics card for displaying metrics"""
    
    def __init__(self, title: str, value: str, icon: str = "", trend: str = "", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.value_text = value
        self.icon_text = icon
        self.trend_text = trend
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup stats card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        if self.icon_text:
            icon_label = QLabel(self.icon_text)
            icon_label.setFont(QFont("Inter", 16))
            icon_label.setStyleSheet("color: #3b82f6;")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.title_text)
        title_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        title_label.setStyleSheet("color: #a1a1aa;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(self.value_text)
        value_label.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #fafafa; margin: 4px 0;")
        layout.addWidget(value_label)
        
        # Trend
        if self.trend_text:
            trend_label = QLabel(self.trend_text)
            trend_label.setFont(QFont("Inter", 11))
            trend_label.setStyleSheet("color: #22c55e;")
            layout.addWidget(trend_label)
    
    def update_value(self, value: str, trend: str = ""):
        """Update the card value and trend"""
        self.value_text = value
        self.trend_text = trend
        # Find and update the value label
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel):
                widget = item.widget()
                if "24" in widget.font().pointSize().__str__():  # Value label
                    widget.setText(value)
                elif trend and "22c55e" in widget.styleSheet():  # Trend label
                    widget.setText(trend)


class QuickActionCard(ShadcnCard):
    """Quick action card with button"""
    
    action_clicked = pyqtSignal()
    
    def __init__(self, title: str, description: str, button_text: str, 
                 icon: str = "", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.description_text = description
        self.button_text = button_text
        self.icon_text = icon
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup quick action card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        if self.icon_text:
            icon_label = QLabel(self.icon_text)
            icon_label.setFont(QFont("Inter", 20))
            icon_label.setStyleSheet("color: #3b82f6;")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.title_text)
        title_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #fafafa;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(self.description_text)
        desc_label.setFont(QFont("Inter", 13))
        desc_label.setStyleSheet("color: #a1a1aa; line-height: 1.5;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Button
        button = ShadcnButton(self.button_text, variant="primary", size="sm")
        button.clicked.connect(self.action_clicked.emit)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)


class RecentActivityCard(ShadcnCard):
    """Recent activity card"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.activities = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup recent activity card UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        
        # Header
        header_label = QLabel("📈 Recent Activity")
        header_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #fafafa; margin-bottom: 8px;")
        self.layout.addWidget(header_label)
        
        # Activity list container
        self.activity_container = QVBoxLayout()
        self.activity_container.setSpacing(8)
        self.layout.addLayout(self.activity_container)
        
        # Add some sample activities
        self.add_activity("🎵", "Audio file uploaded", "2 minutes ago")
        self.add_activity("💬", "Chat session started", "5 minutes ago")
        self.add_activity("📤", "Export completed", "10 minutes ago")
    
    def add_activity(self, icon: str, text: str, time: str):
        """Add an activity item"""
        activity_layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Inter", 14))
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        activity_layout.addWidget(icon_label)
        
        # Text and time
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        text_label = QLabel(text)
        text_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        text_label.setStyleSheet("color: #fafafa;")
        text_layout.addWidget(text_label)
        
        time_label = QLabel(time)
        time_label.setFont(QFont("Inter", 10))
        time_label.setStyleSheet("color: #71717a;")
        text_layout.addWidget(time_label)
        
        activity_layout.addLayout(text_layout)
        activity_layout.addStretch()
        
        self.activity_container.addLayout(activity_layout)


class WelcomeCard(ShadcnCard):
    """Welcome card with gradient background"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_gradient_styling()
    
    def _setup_ui(self):
        """Setup welcome card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Welcome message
        welcome_label = QLabel("👋 Welcome to Audio Chat Studio")
        welcome_label.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #fafafa;")
        layout.addWidget(welcome_label)
        
        # Description
        desc_label = QLabel("Your modern workspace for audio processing, AI chat, and file management. Get started by uploading an audio file or starting a conversation.")
        desc_label.setFont(QFont("Inter", 14))
        desc_label.setStyleSheet("color: #e4e4e7; line-height: 1.6;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        upload_btn = ShadcnButton("📁 Upload File", variant="primary")
        chat_btn = ShadcnButton("💬 Start Chat", variant="secondary")
        
        buttons_layout.addWidget(upload_btn)
        buttons_layout.addWidget(chat_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
    
    def _apply_gradient_styling(self):
        """Apply gradient background styling"""
        self.setStyleSheet("""
            WelcomeCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(59, 130, 246, 0.1),
                    stop:1 rgba(37, 99, 235, 0.05));
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 12px;
            }
        """)


class StatusIndicator(QWidget):
    """Status indicator with colored dot"""
    
    def __init__(self, status: str = "online", text: str = "Ready", parent=None):
        super().__init__(parent)
        self.status = status
        self.text = text
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup status indicator UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Status dot
        self.dot_widget = QWidget()
        self.dot_widget.setFixedSize(8, 8)
        self._update_dot_color()
        layout.addWidget(self.dot_widget)
        
        # Status text
        text_label = QLabel(self.text)
        text_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        text_label.setStyleSheet("color: #a1a1aa;")
        layout.addWidget(text_label)
        
        layout.addStretch()
    
    def _update_dot_color(self):
        """Update dot color based on status"""
        colors = {
            "online": "#22c55e",
            "offline": "#ef4444", 
            "busy": "#f59e0b",
            "away": "#a1a1aa"
        }
        
        color = colors.get(self.status, "#a1a1aa")
        self.dot_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
    
    def set_status(self, status: str, text: str = ""):
        """Update status"""
        self.status = status
        if text:
            self.text = text
        self._update_dot_color()
        # Update text label if needed
        for child in self.findChildren(QLabel):
            if child.text() != self.text:
                child.setText(self.text)
                break