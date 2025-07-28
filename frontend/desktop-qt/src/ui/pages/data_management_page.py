from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QListWidget,
    QFileDialog,
)
from PyQt6.QtCore import Qt

from app_context import settings_service
from services.cloud_storage_service import CloudStorageService


class DataManagementPage(QWidget):
    """Page for managing local and cloud storage."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dataManagementPage")
        self.settings_service = settings_service
        self.cloud_service = CloudStorageService()
        self._setup_ui()
        self._load_credentials()

    # ------------------------------------------------------------------ UI
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
        self.s3_group = self._create_s3_group()
        self.gcs_group = self._create_gcs_group()
        self.azure_group = self._create_azure_group()

        layout.addWidget(self.local_group)
        layout.addWidget(self.s3_group)
        layout.addWidget(self.gcs_group)
        layout.addWidget(self.azure_group)
        layout.addStretch()

    # ---------------------------------------------------------------- Private UI builders
    def _create_local_group(self) -> QGroupBox:
        group = QGroupBox("Local Files")
        vbox = QVBoxLayout(group)
        self.local_files_list = QListWidget()
        vbox.addWidget(self.local_files_list)
        return group

    def _create_s3_group(self) -> QGroupBox:
        group = QGroupBox("AWS S3")
        vbox = QVBoxLayout(group)

        creds = QHBoxLayout()
        creds.addWidget(QLabel("Access Key:"))
        self.s3_access_input = QLineEdit()
        creds.addWidget(self.s3_access_input)
        creds.addWidget(QLabel("Secret:"))
        self.s3_secret_input = QLineEdit()
        self.s3_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        creds.addWidget(self.s3_secret_input)
        self.s3_save_button = QPushButton("Save")
        creds.addWidget(self.s3_save_button)
        vbox.addLayout(creds)

        bucket_row = QHBoxLayout()
        bucket_row.addWidget(QLabel("Bucket:"))
        self.s3_bucket_input = QLineEdit()
        bucket_row.addWidget(self.s3_bucket_input)
        self.s3_refresh_button = QPushButton("Refresh")
        bucket_row.addWidget(self.s3_refresh_button)
        vbox.addLayout(bucket_row)

        self.s3_files_list = QListWidget()
        vbox.addWidget(self.s3_files_list)

        actions = QHBoxLayout()
        self.s3_upload_button = QPushButton("Upload")
        self.s3_download_button = QPushButton("Download")
        actions.addWidget(self.s3_upload_button)
        actions.addWidget(self.s3_download_button)
        vbox.addLayout(actions)

        # connections
        self.s3_save_button.clicked.connect(self._save_s3_credentials)
        self.s3_refresh_button.clicked.connect(self._refresh_s3)
        self.s3_upload_button.clicked.connect(self._upload_s3)
        self.s3_download_button.clicked.connect(self._download_s3)

        return group

    def _create_gcs_group(self) -> QGroupBox:
        group = QGroupBox("Google Cloud Storage")
        vbox = QVBoxLayout(group)

        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Creds JSON:"))
        self.gcs_key_input = QLineEdit()
        key_row.addWidget(self.gcs_key_input)
        self.gcs_save_button = QPushButton("Save")
        key_row.addWidget(self.gcs_save_button)
        vbox.addLayout(key_row)

        bucket_row = QHBoxLayout()
        bucket_row.addWidget(QLabel("Bucket:"))
        self.gcs_bucket_input = QLineEdit()
        bucket_row.addWidget(self.gcs_bucket_input)
        self.gcs_refresh_button = QPushButton("Refresh")
        bucket_row.addWidget(self.gcs_refresh_button)
        vbox.addLayout(bucket_row)

        self.gcs_files_list = QListWidget()
        vbox.addWidget(self.gcs_files_list)

        actions = QHBoxLayout()
        self.gcs_upload_button = QPushButton("Upload")
        self.gcs_download_button = QPushButton("Download")
        actions.addWidget(self.gcs_upload_button)
        actions.addWidget(self.gcs_download_button)
        vbox.addLayout(actions)

        self.gcs_save_button.clicked.connect(self._save_gcs_credentials)
        self.gcs_refresh_button.clicked.connect(self._refresh_gcs)
        self.gcs_upload_button.clicked.connect(self._upload_gcs)
        self.gcs_download_button.clicked.connect(self._download_gcs)

        return group

    def _create_azure_group(self) -> QGroupBox:
        group = QGroupBox("Azure Blob Storage")
        vbox = QVBoxLayout(group)

        conn_row = QHBoxLayout()
        conn_row.addWidget(QLabel("Connection:"))
        self.azure_conn_input = QLineEdit()
        conn_row.addWidget(self.azure_conn_input)
        self.azure_save_button = QPushButton("Save")
        conn_row.addWidget(self.azure_save_button)
        vbox.addLayout(conn_row)

        bucket_row = QHBoxLayout()
        bucket_row.addWidget(QLabel("Container:"))
        self.azure_container_input = QLineEdit()
        bucket_row.addWidget(self.azure_container_input)
        self.azure_refresh_button = QPushButton("Refresh")
        bucket_row.addWidget(self.azure_refresh_button)
        vbox.addLayout(bucket_row)

        self.azure_files_list = QListWidget()
        vbox.addWidget(self.azure_files_list)

        actions = QHBoxLayout()
        self.azure_upload_button = QPushButton("Upload")
        self.azure_download_button = QPushButton("Download")
        actions.addWidget(self.azure_upload_button)
        actions.addWidget(self.azure_download_button)
        vbox.addLayout(actions)

        self.azure_save_button.clicked.connect(self._save_azure_credentials)
        self.azure_refresh_button.clicked.connect(self._refresh_azure)
        self.azure_upload_button.clicked.connect(self._upload_azure)
        self.azure_download_button.clicked.connect(self._download_azure)

        return group

    # --------------------------------------------------------------- Credential loading
    def _load_credentials(self) -> None:
        aws = self.settings_service.get_api_key("aws_s3")
        if aws and ":" in aws:
            access, secret = aws.split(":", 1)
            self.s3_access_input.setText(access)
            self.s3_secret_input.setText(secret)
        gcs = self.settings_service.get_api_key("google_cloud_storage")
        if gcs:
            self.gcs_key_input.setText(gcs)
        azure = self.settings_service.get_api_key("azure_blob")
        if azure:
            self.azure_conn_input.setText(azure)

    # --------------------------------------------------------------- S3
    def _save_s3_credentials(self) -> None:
        access = self.s3_access_input.text().strip()
        secret = self.s3_secret_input.text().strip()
        if access and secret:
            self.settings_service.set_api_key("aws_s3", f"{access}:{secret}")

    def _refresh_s3(self) -> None:
        bucket = self.s3_bucket_input.text().strip()
        if not bucket:
            return
        try:
            files = self.cloud_service.list_files("aws_s3", bucket)
            self.s3_files_list.clear()
            self.s3_files_list.addItems(files)
        except Exception as e:
            print(f"S3 refresh failed: {e}")

    def _upload_s3(self) -> None:
        bucket = self.s3_bucket_input.text().strip()
        if not bucket:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select file to upload")
        if not path:
            return
        try:
            self.cloud_service.upload_file("aws_s3", bucket, path)
            self._refresh_s3()
        except Exception as e:
            print(f"S3 upload failed: {e}")

    def _download_s3(self) -> None:
        bucket = self.s3_bucket_input.text().strip()
        item = self.s3_files_list.currentItem()
        if not bucket or item is None:
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", item.text())
        if not save_path:
            return
        try:
            self.cloud_service.download_file(
                "aws_s3", bucket, item.text(), save_path
            )
        except Exception as e:
            print(f"S3 download failed: {e}")

    # --------------------------------------------------------------- GCS
    def _save_gcs_credentials(self) -> None:
        creds = self.gcs_key_input.text().strip()
        if creds:
            self.settings_service.set_api_key("google_cloud_storage", creds)

    def _refresh_gcs(self) -> None:
        bucket = self.gcs_bucket_input.text().strip()
        if not bucket:
            return
        try:
            files = self.cloud_service.list_files("google_cloud_storage", bucket)
            self.gcs_files_list.clear()
            self.gcs_files_list.addItems(files)
        except Exception as e:
            print(f"GCS refresh failed: {e}")

    def _upload_gcs(self) -> None:
        bucket = self.gcs_bucket_input.text().strip()
        if not bucket:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select file to upload")
        if not path:
            return
        try:
            self.cloud_service.upload_file("google_cloud_storage", bucket, path)
            self._refresh_gcs()
        except Exception as e:
            print(f"GCS upload failed: {e}")

    def _download_gcs(self) -> None:
        bucket = self.gcs_bucket_input.text().strip()
        item = self.gcs_files_list.currentItem()
        if not bucket or item is None:
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", item.text())
        if not save_path:
            return
        try:
            self.cloud_service.download_file(
                "google_cloud_storage", bucket, item.text(), save_path
            )
        except Exception as e:
            print(f"GCS download failed: {e}")

    # --------------------------------------------------------------- Azure
    def _save_azure_credentials(self) -> None:
        conn = self.azure_conn_input.text().strip()
        if conn:
            self.settings_service.set_api_key("azure_blob", conn)

    def _refresh_azure(self) -> None:
        container = self.azure_container_input.text().strip()
        if not container:
            return
        try:
            files = self.cloud_service.list_files("azure_blob", container)
            self.azure_files_list.clear()
            self.azure_files_list.addItems(files)
        except Exception as e:
            print(f"Azure refresh failed: {e}")

    def _upload_azure(self) -> None:
        container = self.azure_container_input.text().strip()
        if not container:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select file to upload")
        if not path:
            return
        try:
            self.cloud_service.upload_file("azure_blob", container, path)
            self._refresh_azure()
        except Exception as e:
            print(f"Azure upload failed: {e}")

    def _download_azure(self) -> None:
        container = self.azure_container_input.text().strip()
        item = self.azure_files_list.currentItem()
        if not container or item is None:
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save file", item.text())
        if not save_path:
            return
        try:
            self.cloud_service.download_file(
                "azure_blob", container, item.text(), save_path
            )
        except Exception as e:
            print(f"Azure download failed: {e}")
