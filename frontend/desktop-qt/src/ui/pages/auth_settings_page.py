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
    QTabWidget,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
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
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom: 2px solid #4CAF50;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🔐 Auth Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self._create_manage_tab()
        self._create_history_tab()

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # connections
        self.save_button.clicked.connect(self._save_api_key)
        self.test_button.clicked.connect(self._test_api_key)
        self.delete_button.clicked.connect(self._delete_api_key)
        self.providers_list.itemClicked.connect(self._provider_selected)

        # update list automatically when keys change
        self.settings_service.api_key_added.connect(lambda *_: self._load_providers())
        self.settings_service.api_key_removed.connect(lambda *_: self._load_providers())

    def _create_manage_tab(self) -> None:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        input_group = QGroupBox("API Key")
        form = QFormLayout(input_group)

        self.provider_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_button = QPushButton("👁️")
        self.show_button.setCheckable(True)
        self.show_button.setFixedWidth(30)
        self.show_button.clicked.connect(self._toggle_visibility)

        key_row = QHBoxLayout()
        key_row.addWidget(self.api_key_input)
        key_row.addWidget(self.show_button)

        form.addRow("Provider", self.provider_input)
        form.addRow("API Key", key_row)

        actions_group = QGroupBox("Actions")
        btn_row = QHBoxLayout(actions_group)
        self.save_button = QPushButton("Save")
        self.test_button = QPushButton("Test")
        self.delete_button = QPushButton("Delete")
        btn_row.addWidget(self.save_button)
        btn_row.addWidget(self.test_button)
        btn_row.addWidget(self.delete_button)

        list_group = QGroupBox("Saved Keys")
        list_layout = QVBoxLayout(list_group)
        self.providers_list = QListWidget()
        list_layout.addWidget(self.providers_list)

        tab_layout.addWidget(input_group)
        tab_layout.addWidget(actions_group)
        tab_layout.addWidget(list_group)
        tab_layout.addStretch()

        self.tab_widget.addTab(tab, "🔑 Keys")

    def _create_history_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Test Time", "Success", "Response Time", "Message"])

        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.history_table)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_history)
        layout.addWidget(refresh_btn)

        layout.addStretch()

        self.tab_widget.addTab(tab, "📜 History")

    def _load_history(self) -> None:
        provider = self.provider_input.text().strip()
        if not provider:
            self.history_table.setRowCount(0)
            return
        history = llm_service.api_key_manager.get_connection_test_history(provider, 20)
        self.history_table.setRowCount(len(history))
        for row, item in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(item["test_time"][:19].replace("T", " ")))
            success_text = "✅" if item["success"] else "❌"
            self.history_table.setItem(row, 1, QTableWidgetItem(success_text))
            resp = f"{item['response_time']:.2f}s" if item["response_time"] else "N/A"
            self.history_table.setItem(row, 2, QTableWidgetItem(resp))
            self.history_table.setItem(row, 3, QTableWidgetItem(item["error_message"] or ""))

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
        self._load_history()

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
            self._load_history()

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
        self._load_history()

