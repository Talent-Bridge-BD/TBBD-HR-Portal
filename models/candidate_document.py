from dataclasses import dataclass
from typing import Optional


@dataclass
class CandidateDocument:
    id: str
    candidate_id: str
    document_type: str
    file_name: str
    blob_container: str
    blob_name: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str = "uploaded"
    uploaded_at: Optional[str] = None
