from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QComboBox,
)
from PyQt6.QtCore import Qt

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
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("👤 Profile")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.avatar_input = QLineEdit()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark_blue.xml", "dark_amber.xml", "dark_teal.xml"])

        form.addRow("Display Name", self.name_input)
        form.addRow("Email", self.email_input)
        form.addRow("Avatar Path", self.avatar_input)
        form.addRow("Theme", self.theme_combo)
        layout.addLayout(form)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_profile)
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _load_profile(self):
        profile = self.profile_service.get_profile("default")
        if profile:
            self.name_input.setText(profile.display_name)
            self.email_input.setText(profile.email)
            self.avatar_input.setText(profile.avatar_path or "")
        theme = self.settings_service.get_setting("theme", "dark_blue.xml")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

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
        self.settings_service.set_setting("theme", self.theme_combo.currentText())
