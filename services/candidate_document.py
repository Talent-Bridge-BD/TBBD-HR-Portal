import os
import re
from io import BytesIO
from typing import Optional
from uuid import uuid4

from models.candidate_document import CandidateDocument
from repositories.candidate_document import CandidateDocumentRepository
from services.candidate_document_storage import CandidateDocumentStorageService


MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "application/pdf": {".pdf"},
    "application/msword": {".doc"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
        ".docx"
    },
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
}


class CandidateDocumentService:
    def __init__(
        self,
        repository: CandidateDocumentRepository,
        storage: CandidateDocumentStorageService,
    ) -> None:
        self.repository = repository
        self.storage = storage

    @staticmethod
    def _safe_filename(file_name: str) -> str:
        name = os.path.basename(file_name).strip()

        if not name:
            raise ValueError("File name is required")

        name = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
        name = re.sub(r"\s+", " ", name).strip()

        if not name:
            raise ValueError("File name is invalid")

        return name[:255]

    @staticmethod
    def _validate_file(
        file_name: str,
        content_type: Optional[str],
        file_size: int,
    ) -> None:
        if file_size <= 0:
            raise ValueError("Document cannot be empty")

        if file_size > MAX_FILE_SIZE:
            raise ValueError("Document size cannot exceed 10 MB")

        extension = os.path.splitext(file_name)[1].lower()

        if not content_type:
            raise ValueError("Document content type is required")

        allowed_extensions = ALLOWED_CONTENT_TYPES.get(
            content_type.lower()
        )

        if not allowed_extensions:
            raise ValueError(
                "Unsupported document type. "
                "Allowed formats: PDF, DOC, DOCX, JPG, JPEG, PNG"
            )

        if extension not in allowed_extensions:
            raise ValueError(
                "File extension does not match the document content type"
            )

    def list_documents(self, user_id: str):
        return self.repository.list_documents(user_id)

    def get_document(
        self,
        user_id: str,
        document_id: str,
    ) -> Optional[CandidateDocument]:
        return self.repository.get_document(
            user_id,
            document_id,
        )

    def create_document(
        self,
        user_id: str,
        document_type: str,
        file_name: str,
        content_type: Optional[str],
        content: bytes,
    ) -> CandidateDocument:
        safe_file_name = self._safe_filename(file_name)

        self._validate_file(
            safe_file_name,
            content_type,
            len(content),
        )

        profile = self.repository.get_candidate_id(user_id)

        if profile is None:
            raise ValueError("Candidate profile has not been created yet")

        candidate_id = profile

        extension = os.path.splitext(safe_file_name)[1].lower()

        blob_name = (
            f"{candidate_id}/"
            f"{uuid4()}"
            f"{extension}"
        )

        container = os.environ.get(
            "CANDIDATE_DOCUMENTS_CONTAINER",
            "candidate-documents",
        )

        self.storage.upload(
            blob_name,
            BytesIO(content),
            content_type,
        )

        try:
            document = self.repository.create_document(
                user_id=user_id,
                document_type=document_type,
                file_name=safe_file_name,
                blob_container=container,
                blob_name=blob_name,
                content_type=content_type,
                file_size=len(content),
            )
        except Exception:
            try:
                self.storage.delete(blob_name)
            except Exception:
                pass
            raise

        return document

    def download_document(
        self,
        user_id: str,
        document_id: str,
    ) -> Optional[tuple[CandidateDocument, bytes]]:
        document = self.repository.get_document(
            user_id,
            document_id,
        )

        if document is None:
            return None

        content = self.storage.download(
            document.blob_name
        )

        return document, content

    def delete_document(
        self,
        user_id: str,
        document_id: str,
    ) -> bool:
        document = self.repository.get_document(
            user_id,
            document_id,
        )

        if document is None:
            return False

        self.storage.delete(
            document.blob_name
        )

        return self.repository.delete_document(
            user_id,
            document_id,
        )
