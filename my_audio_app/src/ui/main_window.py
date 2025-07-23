from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from .widgets.sidebar import Sidebar
from .pages.file_stats_page import FileStatsPage
from .pages.home_page import HomePage


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
        self._register_page("home", HomePage())  # דף הבית החדש
        self._register_page("audio_actions", self._create_dummy_page("⚡ AI Audio Actions"))
        self._register_page("exports", self._create_dummy_page("📤 Audio Exports"))
        self._register_page("file_stats", FileStatsPage())  # דף סטטיסטיקות חדש
        self._register_page("terminal", self._create_dummy_page("🧠 AI Terminal"))
        self._register_page("llm_management", self._create_dummy_page("🧬 LLM Management"))
        self._register_page("auth", self._create_dummy_page("🔐 Auth Settings"))
        self._register_page("profile", self._create_dummy_page("👤 Profile"))
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
