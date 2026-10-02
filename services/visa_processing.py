from repositories.visa_processing import (
    ALLOWED_STATUSES,
    SqlVisaProcessingRepository,
)


class VisaProcessingService:
    def __init__(self, repository: SqlVisaProcessingRepository):
        self.repository = repository

    def list_by_application(
        self,
        application_id: str,
        organization_id: str | None = None,
    ):
        return self.repository.list_by_application(
            application_id=application_id,
            organization_id=organization_id,
        )

    def get(
        self,
        visa_processing_id: str,
        organization_id: str | None = None,
    ):
        return self.repository.get(
            visa_processing_id=visa_processing_id,
            organization_id=organization_id,
        )

    def create(
        self,
        application_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date=None,
        approval_date=None,
        expiry_date=None,
        status: str = "Pending",
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ):
        self._validate_status(status)

        return self.repository.create(
            application_id=application_id,
            visa_type=visa_type,
            visa_number=visa_number,
            application_number=application_number,
            submission_date=submission_date,
            approval_date=approval_date,
            expiry_date=expiry_date,
            status=status,
            sponsor_name=sponsor_name,
            sponsor_reference=sponsor_reference,
            notes=notes,
        )

    def update(
        self,
        visa_processing_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date=None,
        approval_date=None,
        expiry_date=None,
        status: str | None = None,
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ):
        if status is not None:
            self._validate_status(status)

        return self.repository.update(
            visa_processing_id=visa_processing_id,
            visa_type=visa_type,
            visa_number=visa_number,
            application_number=application_number,
            submission_date=submission_date,
            approval_date=approval_date,
            expiry_date=expiry_date,
            status=status,
            sponsor_name=sponsor_name,
            sponsor_reference=sponsor_reference,
            notes=notes,
        )

    @staticmethod
    def _validate_status(status: str):
        if status not in ALLOWED_STATUSES:
            raise ValueError(
                "Invalid visa processing status. "
                f"Allowed values: {', '.join(sorted(ALLOWED_STATUSES))}"
            )
