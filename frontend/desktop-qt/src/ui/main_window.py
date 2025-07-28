from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from .widgets.sidebar import Sidebar
from .pages.file_stats_page import FileStatsPage
from .pages.home_page import HomePage
from .pages.audio_export_page import AudioExportPage
from .pages.llm_manager_page import LLMManagerPage
from .pages.auth_settings_page import AuthSettingsPage
from .pages.profile_page import ProfilePage
from .pages.data_management_page import DataManagementPage
from .components.notifications import NotificationManager, NotificationType


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Audio Chat Studio")
        self.resize(1400, 900)
        
        # Set window properties
        self.setMinimumSize(1000, 700)
        
        # Main container widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        # Content area
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Notification manager
        self.notification_manager = NotificationManager(central_widget)

        # Pages
        self.pages = {}
        self._register_page("home", HomePage())
        self._register_page("audio_actions", self._create_dummy_page("⚡ AI Audio Actions"))
        self._register_page("exports", AudioExportPage())
        self._register_page("file_stats", FileStatsPage())
        self._register_page("terminal", self._create_dummy_page("🧠 AI Terminal"))
        self._register_page("llm_management", LLMManagerPage())
        self._register_page("auth", AuthSettingsPage())
        self._register_page("profile", ProfilePage())
        self._register_page("data_management", DataManagementPage())

        # Connect navigation
        self.sidebar.page_changed.connect(self.set_current_page)

        # Load default page
        self.set_current_page("home")
        self.sidebar.set_active_page("home")
        
        # Show welcome notification after a short delay
        QTimer.singleShot(1000, self._show_welcome_notification)

    def _register_page(self, name, widget):
        self.stack.addWidget(widget)
        self.pages[name] = widget

    def set_current_page(self, page_name):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])

    def _create_dummy_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Main title
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        label.setStyleSheet("""
            QLabel {
                color: #fafafa;
                margin-bottom: 16px;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        layout.addWidget(label)
        
        # Subtitle
        subtitle = QLabel("Coming Soon")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Inter", 18, QFont.Weight.Medium))
        subtitle.setStyleSheet("""
            QLabel {
                color: #3b82f6;
                margin-bottom: 12px;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        layout.addWidget(subtitle)
        
        # Description
        description = QLabel("This feature is currently under development.\nCheck back soon for updates!")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont("Inter", 14))
        description.setStyleSheet("""
            QLabel {
                color: #a1a1aa;
                line-height: 1.6;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        layout.addWidget(description)
        
        return page
    
    def _show_welcome_notification(self):
        """Show welcome notification"""
        self.notification_manager.show_success(
            "🎉 Welcome to Audio Chat Studio! Your modern audio processing workspace is ready.",
            duration=6000
        )
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        # Update notification manager position
        if hasattr(self, 'notification_manager'):
            self.notification_manager.resizeEvent(event)
