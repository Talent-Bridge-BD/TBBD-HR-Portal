from __future__ import annotations

from io import BytesIO
import os
from uuid import uuid4

from models.candidate_document import CandidateDocument
from repositories.blob_storage import BlobStorageRepository
from repositories.candidate_document import CandidateDocumentRepository


class CandidateDocumentService:
    MAX_FILE_SIZE = 10 * 1024 * 1024

    ALLOWED_DOCUMENT_TYPES = {
        "passport": {
            "application/pdf",
            "image/jpeg",
            "image/png",
        },
        "resume": {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        },
    }

    @staticmethod
    def _sanitize_file_name(file_name: str) -> str:
        name = os.path.basename(file_name or "document")
        name = name.replace("\r", "_")
        name = name.replace("\n", "_")
        name = name.replace('"', "_")
        name = name.replace("\\", "_")
        name = name.strip()

        if not name:
            return "document"

        return name[:255]

    @staticmethod
    def _validate_file_signature(
        content_type: str,
        file_bytes: bytes,
    ) -> None:
        signatures = {
            "application/pdf": (b"%PDF-",),
            "image/jpeg": (b"\xff\xd8\xff",),
            "image/png": (b"\x89PNG\r\n\x1a\n",),
            "application/msword": (
                b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",
            ),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
                b"PK\x03\x04",
            ),
        }

        expected = signatures.get(content_type)

        if expected is None:
            raise ValueError("Unsupported file type")

        if not any(file_bytes.startswith(signature) for signature in expected):
            raise ValueError("File content does not match the declared file type")

    def __init__(
        self,
        document_repository: CandidateDocumentRepository,
        blob_repository: BlobStorageRepository,
    ):
        self.document_repository = document_repository
        self.blob_repository = blob_repository

    def list_documents(
        self,
        candidate_id: str,
    ) -> list[CandidateDocument]:
        return self.document_repository.list_documents(candidate_id)

    def upload_document(
        self,
        candidate_id: str,
        document_type: str,
        file_name: str,
        content_type: str,
        file_bytes: bytes,
    ) -> CandidateDocument:
        allowed_types = self.ALLOWED_DOCUMENT_TYPES.get(document_type)

        if allowed_types is None:
            raise ValueError("Unsupported document type")

        if content_type not in allowed_types:
            raise ValueError("Unsupported file type")

        if not file_bytes:
            raise ValueError("File is empty")

        if len(file_bytes) > self.MAX_FILE_SIZE:
            raise ValueError("File exceeds the 10 MB limit")

        self._validate_file_signature(
            content_type,
            file_bytes,
        )

        safe_file_name = self._sanitize_file_name(file_name)

        extension = (
            safe_file_name.rsplit(".", 1)[-1].lower()
            if "." in safe_file_name
            else ""
        )

        if not extension:
            raise ValueError("File extension is required")

        allowed_extensions = {
            "application/pdf": {"pdf"},
            "image/jpeg": {"jpg", "jpeg"},
            "image/png": {"png"},
            "application/msword": {"doc"},
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
                "docx"
            },
        }

        expected_extensions = allowed_extensions.get(content_type, set())

        if extension not in expected_extensions:
            raise ValueError(
                "File extension does not match the declared file type"
            )

        blob_name = (
            f"candidates/{candidate_id}/"
            f"{document_type}/{uuid4()}.{extension}"
        )

        self.blob_repository.upload(
            blob_name,
            BytesIO(file_bytes),
            content_type,
        )

        try:
            document, old_document = (
                self.document_repository.replace_document(
                    candidate_id=candidate_id,
                    document_type=document_type,
                    file_name=safe_file_name,
                    blob_container=self.blob_repository.container_name,
                    blob_name=blob_name,
                    content_type=content_type,
                    file_size=len(file_bytes),
                )
            )
        except Exception:
            try:
                self.blob_repository.delete(blob_name)
            except Exception:
                pass
            raise

        if old_document is not None:
            try:
                self.blob_repository.delete(old_document.blob_name)
            except Exception:
                # The new document is already authoritative in SQL.
                # The old Blob can be cleaned up separately if deletion
                # temporarily fails.
                pass

        return document

    def delete_document(
        self,
        candidate_id: str,
        document_id: str,
    ) -> CandidateDocument | None:
        document = self.document_repository.get_document(
            candidate_id,
            document_id,
        )

        if document is None:
            return None

        deleted = self.document_repository.delete_document(
            candidate_id,
            document_id,
        )

        if deleted is None:
            return None

        try:
            self.blob_repository.delete(document.blob_name)
        except Exception:
            # SQL metadata is already removed. A temporary Blob deletion
            # failure must not make the API report that the document remains.
            pass

        return deleted
