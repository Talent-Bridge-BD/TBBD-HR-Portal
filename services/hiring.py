from typing import Optional

from models.hiring import HiringApplication
from repositories.hiring import HiringRepository


class HiringService:

    def __init__(self, repository: HiringRepository):
        self.repository = repository

    def list_hiring_applications(
        self,
        organization_id: str,
    ) -> list[HiringApplication]:
        return self.repository.list_hiring_applications(
            organization_id,
        )

    def list_ready_for_hiring(
        self,
        organization_id: str,
    ) -> list[HiringApplication]:
        return self.repository.list_ready_for_hiring(
            organization_id,
        )

    def get_hiring_application(
        self,
        organization_id: str,
        application_id: str,
    ) -> Optional[HiringApplication]:
        return self.repository.get_hiring_application(
            organization_id,
            application_id,
        )

    def get_readiness(
        self,
        organization_id: str,
        application_id: str,
    ):
        return self.repository.get_readiness(
            organization_id,
            application_id,
        )

    def create_hiring_record(
        self,
        organization_id: str,
        application_id: str,
        readiness_source: str,
        waiver_reason: Optional[str] = None,
    ):
        readiness = self.repository.get_readiness(
            organization_id,
            application_id,
        )

        if readiness is None:
            raise ValueError("Application not found.")

        application_status = str(
            readiness.get("application_status") or ""
        ).lower()

        if application_status != "shortlisted":
            raise ValueError(
                "Only shortlisted candidates can become ready for hiring."
            )

        existing = self.repository.get_hiring_record(
            organization_id,
            application_id,
        )

        if existing is not None:
            raise ValueError(
                "This candidate is already in the hiring workflow."
            )

        if readiness_source == "interview_pass":
            if readiness.get("readiness_source") != "interview_pass":
                raise ValueError(
                    "A completed interview with a Pass outcome is required."
                )

        elif readiness_source == "trade_test_pass":
            if readiness.get("readiness_source") != "trade_test_pass":
                raise ValueError(
                    "A completed trade test with a Pass result is required."
                )

        elif readiness_source == "waived":
            if not waiver_reason or not waiver_reason.strip():
                raise ValueError(
                    "A waiver reason is required."
                )

        else:
            raise ValueError(
                "Invalid hiring readiness source."
            )

        return self.repository.create_hiring_record(
            organization_id,
            application_id,
            readiness_source,
            waiver_reason.strip()
            if waiver_reason
            else None,
        )

    def get_hiring_record(
        self,
        organization_id: str,
        application_id: str,
    ):
        return self.repository.get_hiring_record(
            organization_id,
            application_id,
        )

    def list_candidate_offers(
        self,
        candidate_id: str,
    ):
        return self.repository.list_candidate_offers(
            candidate_id,
        )

    def accept_candidate_offer(
        self,
        candidate_id: str,
        offer_id: str,
    ):
        if not offer_id or not offer_id.strip():
            raise ValueError("Offer ID is required.")

        return self.repository.accept_candidate_offer(
            candidate_id,
            offer_id,
        )

    def create_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_title: str,
        employment_type: Optional[str] = None,
        salary_amount: Optional[float] = None,
        salary_currency: Optional[str] = None,
        start_date: Optional[str] = None,
        offer_expiry_date: Optional[str] = None,
        terms_and_conditions: Optional[str] = None,
    ):
        hiring_record = self.repository.get_hiring_record(
            organization_id,
            application_id,
        )

        if hiring_record is None:
            raise ValueError(
                "Candidate is not ready for hiring."
            )

        if hiring_record.get("status") != "ready_for_hiring":
            raise ValueError(
                "An offer can only be created for a candidate who is Ready for Hiring."
            )

        if not offer_title or not offer_title.strip():
            raise ValueError(
                "Offer title is required."
            )

        return self.repository.create_offer(
            organization_id=organization_id,
            application_id=application_id,
            offer_title=offer_title.strip(),
            employment_type=employment_type.strip()
            if employment_type
            else None,
            salary_amount=salary_amount,
            salary_currency=salary_currency.strip()
            if salary_currency
            else None,
            start_date=start_date,
            offer_expiry_date=offer_expiry_date,
            terms_and_conditions=terms_and_conditions.strip()
            if terms_and_conditions
            else None,
        )

    def update_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
        offer_title: Optional[str] = None,
        employment_type: Optional[str] = None,
        salary_amount: Optional[float] = None,
        salary_currency: Optional[str] = None,
        start_date: Optional[str] = None,
        offer_expiry_date: Optional[str] = None,
        terms_and_conditions: Optional[str] = None,
        status: Optional[str] = None,
    ):
        allowed_statuses = {
            "Draft",
            "Sent",
            "Accepted",
            "Rejected",
            "Withdrawn",
        }

        if status is not None and status not in allowed_statuses:
            raise ValueError(
                "Invalid offer status."
            )

        if offer_title is not None and not offer_title.strip():
            raise ValueError(
                "Offer title cannot be empty."
            )

        if status is None:
            raise ValueError(
                "Offer status is required when updating an offer."
            )

        if offer_title is None:
            raise ValueError(
                "Offer title is required when updating an offer."
            )

        return self.repository.update_offer(
            organization_id=organization_id,
            application_id=application_id,
            offer_id=offer_id,
            status=status,
            offer_title=offer_title.strip(),
            employment_type=employment_type.strip()
            if employment_type is not None
            else None,
            salary_amount=salary_amount,
            salary_currency=salary_currency.strip()
            if salary_currency is not None
            else None,
            start_date=start_date,
            offer_expiry_date=offer_expiry_date,
            terms_and_conditions=terms_and_conditions.strip()
            if terms_and_conditions is not None
            else None,
        )

    def send_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
    ):
        if not offer_id or not offer_id.strip():
            raise ValueError("Offer ID is required.")

        return self.repository.send_offer(
            organization_id=organization_id,
            application_id=application_id,
            offer_id=offer_id,
        )

    def get_offer(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
    ):
        return self.repository.get_offer(
            organization_id,
            application_id,
            offer_id,
        )

    def hire(
        self,
        organization_id: str,
        application_id: str,
        offer_id: str,
    ):
        hiring_record = self.repository.get_hiring_record(
            organization_id,
            application_id,
        )

        if hiring_record is None:
            raise ValueError(
                "Candidate is not in the hiring workflow."
            )

        if hiring_record.get("status") != "offered":
            raise ValueError(
                "Candidate can only be hired after an offer is accepted."
            )

        if not offer_id or not offer_id.strip():
            raise ValueError(
                "Accepted offer ID is required."
            )

        return self.repository.hire(
            organization_id,
            application_id,
            offer_id,
        )
