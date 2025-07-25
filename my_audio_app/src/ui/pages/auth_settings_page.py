from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from app_context import settings_service, llm_service


class AuthSettingsPage(QWidget):
    """Simple page for managing API keys using :class:`SettingsService`."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("authSettingsPage")
        self.settings_service = settings_service

        self._setup_ui()
        self._load_providers()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #121212;
                color: white;
            }
            QLineEdit, QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 4px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🔐 Auth Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        self.provider_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Show/Hide button for API key
        self.show_button = QPushButton("👁️")
        self.show_button.setCheckable(True)
        self.show_button.setFixedWidth(30)
        self.show_button.clicked.connect(self._toggle_visibility)

        key_row = QHBoxLayout()
        key_row.addWidget(self.api_key_input)
        key_row.addWidget(self.show_button)

        form.addRow("Provider", self.provider_input)
        form.addRow("API Key", key_row)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.test_button = QPushButton("Test")
        self.delete_button = QPushButton("Delete")
        btn_row.addWidget(self.save_button)
        btn_row.addWidget(self.test_button)
        btn_row.addWidget(self.delete_button)
        layout.addLayout(btn_row)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.providers_list = QListWidget()
        layout.addWidget(QLabel("Saved Keys:"))
        layout.addWidget(self.providers_list)

        # connections
        self.save_button.clicked.connect(self._save_api_key)
        self.test_button.clicked.connect(self._test_api_key)
        self.delete_button.clicked.connect(self._delete_api_key)
        self.providers_list.itemClicked.connect(self._provider_selected)

        # update list automatically when keys change
        self.settings_service.api_key_added.connect(lambda *_: self._load_providers())
        self.settings_service.api_key_removed.connect(lambda *_: self._load_providers())

    def _load_providers(self) -> None:
        self.providers_list.clear()
        providers = self.settings_service.get_all_api_key_providers()
        for provider in providers:
            masked = self.settings_service.get_api_key_masked(provider) or ""
            item = QListWidgetItem(f"{provider}: {masked}")
            item.setData(Qt.ItemDataRole.UserRole, provider)
            self.providers_list.addItem(item)

    def _provider_selected(self, item: QListWidgetItem) -> None:
        provider = item.data(Qt.ItemDataRole.UserRole)
        key = self.settings_service.get_api_key(provider) or ""
        self.provider_input.setText(provider)
        self.api_key_input.setText(key)

    def _save_api_key(self) -> None:
        provider = self.provider_input.text().strip()
        key = self.api_key_input.text().strip()
        if provider and key:
            self.settings_service.set_api_key(provider, key)
            self._load_providers()

    def _delete_api_key(self) -> None:
        provider = self.provider_input.text().strip()
        if provider:
            self.settings_service.delete_api_key(provider)
            self.provider_input.clear()
            self.api_key_input.clear()
            self._load_providers()

    def _toggle_visibility(self) -> None:
        if self.show_button.isChecked():
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_button.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_button.setText("👁️")

    def _test_api_key(self) -> None:
        provider = self.provider_input.text().strip()
        key = self.api_key_input.text().strip()
        if not provider or not key:
            QMessageBox.warning(self, "Missing Data", "Provider and API key are required")
            return
        success, message, _time = llm_service.api_key_manager.test_api_key_connection(provider, key)
        icon = "✅" if success else "❌"
        self.status_label.setText(f"{icon} {message}")

