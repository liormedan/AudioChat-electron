from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QComboBox,
    QTabWidget,
    QApplication,
)
from PyQt6.QtCore import Qt
from qt_material import apply_stylesheet, list_themes
import os
import glob

from app_context import profile_service, settings_service
from models.user_profile import UserProfile
from datetime import datetime


class ProfilePage(QWidget):
    """Simple profile management page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("profilePage")
        self.profile_service = profile_service
        self.settings_service = settings_service
        self._setup_ui()
        self._load_profile()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #121212;
                color: white;
            }

            QLineEdit, QPushButton, QComboBox {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }

            QPushButton:hover {
                background-color: #444;
            }

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
            }

            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("👤 Profile")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # General information tab
        general_tab = QWidget()
        general_form = QFormLayout(general_tab)
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.avatar_input = QLineEdit()
        general_form.addRow("Display Name", self.name_input)
        general_form.addRow("Email", self.email_input)
        general_form.addRow("Avatar Path", self.avatar_input)
        self.tab_widget.addTab(general_tab, "General Info")

        # Preferences tab
        preferences_tab = QWidget()
        preferences_form = QFormLayout(preferences_tab)
        self.theme_combo = QComboBox()

        # Import theme service
        from services.theme_service import theme_service
        self.theme_service = theme_service

        # Get all available themes
        available_themes = self.theme_service.get_available_themes()
        
        # Add themes to combo box with nice display names
        theme_display_names = {
            "kiro_modern_dark": "🌙 Kiro Modern Dark",
            "kiro_modern_light": "☀️ Kiro Modern Light", 
            "dark_blue.xml": "🔵 Classic Dark Blue",
            "light_blue.xml": "🔷 Classic Light Blue",
            "dark_teal.xml": "🟢 Dark Teal",
            "light_teal.xml": "🟦 Light Teal",
        }
        
        for theme in sorted(available_themes):
            display_name = theme_display_names.get(theme, theme)
            self.theme_combo.addItem(display_name, theme)
        
        self.theme_combo.currentTextChanged.connect(self._apply_theme)
        preferences_form.addRow("Theme", self.theme_combo)
        self.tab_widget.addTab(preferences_tab, "Preferences")

        layout.addWidget(self.tab_widget)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_profile)
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _load_profile(self):
        profile = self.profile_service.get_profile("default")
        if profile:
            self.name_input.setText(profile.display_name)
            self.email_input.setText(profile.email)
            self.avatar_input.setText(profile.avatar_path or "")
        
        # Load current theme
        current_theme = self.settings_service.get_setting("theme", "kiro_modern_dark")
        
        # Find the theme in combo box by data (not display text)
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break

    def _save_profile(self):
        profile = UserProfile(
            id="default",
            display_name=self.name_input.text().strip(),
            email=self.email_input.text().strip(),
            avatar_path=self.avatar_input.text().strip() or None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.profile_service.save_profile(profile)
        
        # Save current theme
        current_index = self.theme_combo.currentIndex()
        if current_index >= 0:
            theme_name = self.theme_combo.itemData(current_index)
            if theme_name:
                self.settings_service.set_setting("theme", theme_name)

    def _apply_theme(self, display_name: str) -> None:
        """Apply the selected theme immediately and persist it."""
        # Get the actual theme name from the combo box data
        current_index = self.theme_combo.currentIndex()
        if current_index >= 0:
            theme_name = self.theme_combo.itemData(current_index)
            if theme_name:
                self.theme_service.apply_theme(theme_name)
                self.settings_service.set_setting("theme", theme_name)
