from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserProfile:
    user_id: str
    full_name: str = ""
    primary_email: str = ""
    phone: str = ""
    office_phone: str = ""
    organization_email: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
