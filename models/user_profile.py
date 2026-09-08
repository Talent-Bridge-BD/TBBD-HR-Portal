from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserProfile:
    user_id: str
    full_name: str = ""
    phone: str = ""
    organization_email: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
