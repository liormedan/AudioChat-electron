from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from .widgets.sidebar import Sidebar
from .pages.file_stats_page import FileStatsPage
from .pages.home_page import HomePage
from .pages.audio_export_page import AudioExportPage
from .pages.llm_manager_page import LLMManagerPage
from .pages.auth_settings_page import AuthSettingsPage
from .pages.profile_page import ProfilePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Chat Studio")
        self.resize(1200, 800)

        # Main container widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #121212;")
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
        self._register_page("database", self._create_dummy_page("🗃️ Database Management"))

        # Connect navigation
        self.sidebar.page_changed.connect(self.set_current_page)

        # Load default page
        self.set_current_page("home")
        self.sidebar.set_active_page("home")

    def _register_page(self, name, widget):
        self.stack.addWidget(widget)
        self.pages[name] = widget

    def set_current_page(self, page_name):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])

    def _create_dummy_page(self, title):
        page = QWidget()
        page.setStyleSheet("background-color: #121212;")
        layout = QVBoxLayout(page)
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(label)
        return page
