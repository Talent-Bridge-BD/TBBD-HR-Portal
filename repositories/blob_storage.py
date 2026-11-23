from __future__ import annotations

import os
from typing import BinaryIO

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings


class BlobStorageRepository:
    """
    Private Azure Blob Storage access for candidate documents.

    Authentication uses Microsoft Entra ID through DefaultAzureCredential.
    """

    def __init__(
        self,
        account_name: str | None = None,
        container_name: str | None = None,
    ):
        self.account_name = account_name or os.environ.get(
            "DOCUMENT_STORAGE_ACCOUNT",
            "tbbdhrcandidatedocssea",
        )
        self.container_name = container_name or os.environ.get(
            "DOCUMENT_STORAGE_CONTAINER",
            "candidate-documents",
        )

        self.credential = DefaultAzureCredential()

        self.service_client = BlobServiceClient(
            account_url=(
                f"https://{self.account_name}.blob.core.windows.net"
            ),
            credential=self.credential,
        )

        self.container_client = (
            self.service_client.get_container_client(
                self.container_name
            )
        )

    def upload(
        self,
        blob_name: str,
        file_obj: BinaryIO,
        content_type: str | None = None,
    ) -> None:
        blob_client = self.container_client.get_blob_client(blob_name)

        blob_client.upload_blob(
            file_obj,
            overwrite=True,
            content_settings=(
                ContentSettings(content_type=content_type)
                if content_type
                else None
            ),
        )

    def download(self, blob_name: str) -> bytes:
        blob_client = self.container_client.get_blob_client(blob_name)

        return blob_client.download_blob().readall()

    def delete(self, blob_name: str) -> None:
        blob_client = self.container_client.get_blob_client(blob_name)

        blob_client.delete_blob(
            delete_snapshots="include",
        )

    def exists(self, blob_name: str) -> bool:
        blob_client = self.container_client.get_blob_client(blob_name)

        return blob_client.exists()
