from datetime import datetime
from typing import Optional

from models.interview import EmployerInterview
from repositories.interview import InterviewRepository


class InterviewService:

    def __init__(self, repository: InterviewRepository):
        self.repository = repository

    def list_interviews(
        self,
        organization_id: str,
    ) -> list[EmployerInterview]:
        return self.repository.list_interviews(
            organization_id,
        )

    def get_interview(
        self,
        organization_id: str,
        interview_id: str,
    ) -> Optional[EmployerInterview]:
        return self.repository.get_interview(
            organization_id,
            interview_id,
        )

    def create_interview(
        self,
        organization_id: str,
        application_id: str,
        scheduled_start: datetime,
        scheduled_end: Optional[datetime],
        interview_type: str,
        location_or_link: str,
        interviewer_name: str,
        notes: str,
    ) -> EmployerInterview:
        return self.repository.create_interview(
            organization_id,
            application_id,
            scheduled_start,
            scheduled_end,
            interview_type,
            location_or_link,
            interviewer_name,
            notes,
        )

    def update_interview(
        self,
        organization_id: str,
        interview_id: str,
        scheduled_start: datetime,
        scheduled_end: Optional[datetime],
        interview_type: str,
        location_or_link: str,
        interviewer_name: str,
        notes: str,
        status: str,
    ) -> Optional[EmployerInterview]:
        return self.repository.update_interview(
            organization_id,
            interview_id,
            scheduled_start,
            scheduled_end,
            interview_type,
            location_or_link,
            interviewer_name,
            notes,
            status,
        )
