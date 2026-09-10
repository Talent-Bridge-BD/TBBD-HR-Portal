import os
from io import BytesIO
from typing import BinaryIO

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


STORAGE_ACCOUNT = os.environ.get(
    "CANDIDATE_DOCUMENTS_STORAGE_ACCOUNT",
    "tbbdhrcandidatedocssea",
)
CONTAINER = os.environ.get(
    "CANDIDATE_DOCUMENTS_CONTAINER",
    "candidate-documents",
)


class CandidateDocumentStorageService:
    def __init__(self) -> None:
        self.credential = DefaultAzureCredential()

        endpoint = (
            f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"
        )

        self.client = BlobServiceClient(
            account_url=endpoint,
            credential=self.credential,
        )

        self.container_client = self.client.get_container_client(
            CONTAINER
        )

    def upload(
        self,
        blob_name: str,
        data: BinaryIO,
        content_type: str | None = None,
    ) -> None:
        blob_client = self.container_client.get_blob_client(blob_name)

        kwargs = {}

        if content_type:
            from azure.storage.blob import ContentSettings

            kwargs["content_settings"] = ContentSettings(
                content_type=content_type
            )

        blob_client.upload_blob(
            data,
            overwrite=False,
            **kwargs,
        )

    def download(self, blob_name: str) -> bytes:
        blob_client = self.container_client.get_blob_client(blob_name)

        downloader = blob_client.download_blob()

        return downloader.readall()

    def delete(self, blob_name: str) -> None:
        blob_client = self.container_client.get_blob_client(blob_name)

        blob_client.delete_blob(
            delete_snapshots="include"
        )

    def exists(self, blob_name: str) -> bool:
        blob_client = self.container_client.get_blob_client(blob_name)

        return blob_client.exists()
