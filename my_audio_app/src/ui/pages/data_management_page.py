from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QLineEdit, QPushButton, QListWidget
)
from PyQt6.QtCore import Qt


class DataManagementPage(QWidget):
    """Page for managing local and cloud storage."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dataManagementPage")
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #121212;
                color: white;
            }
            QGroupBox {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
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
        layout.setSpacing(15)

        title = QLabel("🗄️ Data Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)

        self.local_group = self._create_local_group()
        self.gcs_group = self._create_gcs_group()
        self.onedrive_group = self._create_onedrive_group()

        layout.addWidget(self.local_group)
        layout.addWidget(self.gcs_group)
        layout.addWidget(self.onedrive_group)
        layout.addStretch()

    def _create_local_group(self) -> QGroupBox:
        group = QGroupBox("Local Files")
        vbox = QVBoxLayout(group)
        self.local_files_list = QListWidget()
        vbox.addWidget(self.local_files_list)
        return group

    def _create_gcs_group(self) -> QGroupBox:
        group = QGroupBox("Google Cloud Storage")
        vbox = QVBoxLayout(group)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("API Key:"))
        self.gcs_key_input = QLineEdit()
        controls.addWidget(self.gcs_key_input)
        self.gcs_connect_button = QPushButton("Connect")
        controls.addWidget(self.gcs_connect_button)
        vbox.addLayout(controls)

        self.gcs_files_list = QListWidget()
        vbox.addWidget(self.gcs_files_list)
        return group

    def _create_onedrive_group(self) -> QGroupBox:
        group = QGroupBox("OneDrive")
        vbox = QVBoxLayout(group)

        controls = QHBoxLayout()
        self.onedrive_login_button = QPushButton("Login")
        controls.addWidget(self.onedrive_login_button)
        controls.addStretch()
        vbox.addLayout(controls)

        self.onedrive_files_list = QListWidget()
        vbox.addWidget(self.onedrive_files_list)
        return group
