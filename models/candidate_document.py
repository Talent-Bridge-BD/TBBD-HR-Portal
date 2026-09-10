from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CandidateDocument:
    id: str
    candidate_id: str
    document_type: str
    file_name: str
    blob_container: str
    blob_name: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str = "submitted"
    uploaded_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
