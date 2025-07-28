"""Simplified cloud storage service.

Provides basic upload and download helpers for
AWS S3, Google Cloud Storage and Azure Blob Storage.
Credentials are loaded from SettingsService using provider
names 'aws_s3', 'google_cloud_storage' and 'azure_blob'.
"""

from __future__ import annotations

import os
from typing import Optional, List

from app_context import settings_service


class CloudStorageService:
    """Manage uploads/downloads to multiple cloud providers."""

    def __init__(self) -> None:
        self.settings_service = settings_service

    # Helpers to lazily import heavy packages
    def _get_s3_client(self):
        try:
            import boto3  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("boto3 not installed") from exc

        creds = self.settings_service.get_api_key("aws_s3")
        if not creds:
            raise RuntimeError("AWS credentials not configured")
        access_key, secret = creds.split(":", 1)
        return boto3.client(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret
        )

    def _get_gcs_client(self):
        try:
            from google.cloud import storage  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("google-cloud-storage not installed") from exc

        creds_json = self.settings_service.get_api_key("google_cloud_storage")
        if not creds_json:
            raise RuntimeError("GCS credentials not configured")
        return storage.Client.from_service_account_json(creds_json)

    def _get_azure_client(self, container: str):
        try:
            from azure.storage.blob import BlobServiceClient  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("azure-storage-blob not installed") from exc

        conn_str = self.settings_service.get_api_key("azure_blob")
        if not conn_str:
            raise RuntimeError("Azure credentials not configured")
        service = BlobServiceClient.from_connection_string(conn_str)
        return service.get_container_client(container)

    # Public API
    def list_files(self, provider: str, bucket: str) -> List[str]:
        if provider == "aws_s3":
            s3 = self._get_s3_client()
            resp = s3.list_objects_v2(Bucket=bucket)
            return [item["Key"] for item in resp.get("Contents", [])]
        if provider == "google_cloud_storage":
            client = self._get_gcs_client()
            blobs = client.list_blobs(bucket)
            return [b.name for b in blobs]
        if provider == "azure_blob":
            container_client = self._get_azure_client(bucket)
            return [b.name for b in container_client.list_blobs()]
        raise ValueError(f"Unknown provider {provider}")

    def upload_file(
        self, provider: str, bucket: str, local_path: str, remote_path: Optional[str] = None
    ) -> None:
        remote_path = remote_path or os.path.basename(local_path)
        if provider == "aws_s3":
            s3 = self._get_s3_client()
            s3.upload_file(local_path, bucket, remote_path)
            return
        if provider == "google_cloud_storage":
            client = self._get_gcs_client()
            bucket_obj = client.bucket(bucket)
            blob = bucket_obj.blob(remote_path)
            blob.upload_from_filename(local_path)
            return
        if provider == "azure_blob":
            container_client = self._get_azure_client(bucket)
            with open(local_path, "rb") as f:
                container_client.upload_blob(name=remote_path, data=f)
            return
        raise ValueError(f"Unknown provider {provider}")

    def download_file(
        self, provider: str, bucket: str, remote_path: str, local_path: str
    ) -> None:
        if provider == "aws_s3":
            s3 = self._get_s3_client()
            s3.download_file(bucket, remote_path, local_path)
            return
        if provider == "google_cloud_storage":
            client = self._get_gcs_client()
            bucket_obj = client.bucket(bucket)
            blob = bucket_obj.blob(remote_path)
            blob.download_to_filename(local_path)
            return
        if provider == "azure_blob":
            container_client = self._get_azure_client(bucket)
            with open(local_path, "wb") as f:
                download_stream = container_client.download_blob(remote_path)
                f.write(download_stream.readall())
            return
        raise ValueError(f"Unknown provider {provider}")
