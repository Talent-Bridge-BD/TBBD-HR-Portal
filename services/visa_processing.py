from datetime import date

from repositories.visa_processing import SqlVisaProcessingRepository


class VisaProcessingService:

    ALLOWED_STATUSES = {
        "Pending",
        "Submitted",
        "Processing",
        "Approved",
        "Rejected",
        "Expired",
    }

    def __init__(
        self,
        repository: SqlVisaProcessingRepository,
    ):
        self.repository = repository

    def list_by_application(
        self,
        organization_id: str,
        application_id: str,
    ):
        return self.repository.list_by_application(
            organization_id,
            application_id,
        )

    def create(
        self,
        organization_id: str,
        application_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date: date | None = None,
        approval_date: date | None = None,
        expiry_date: date | None = None,
        status: str = "Pending",
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ):
        self._validate_status(status)

        return self.repository.create(
            organization_id=organization_id,
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

    def get(
        self,
        organization_id: str,
        visa_processing_id: str,
    ):
        return self.repository.get(
            organization_id,
            visa_processing_id,
        )

    def update(
        self,
        organization_id: str,
        visa_processing_id: str,
        visa_type: str | None = None,
        visa_number: str | None = None,
        application_number: str | None = None,
        submission_date: date | None = None,
        approval_date: date | None = None,
        expiry_date: date | None = None,
        status: str | None = None,
        sponsor_name: str | None = None,
        sponsor_reference: str | None = None,
        notes: str | None = None,
    ):
        if status is not None:
            self._validate_status(status)

        if approval_date is not None and submission_date is not None:
            if approval_date < submission_date:
                raise ValueError(
                    "Approval date cannot be earlier than submission date"
                )

        if expiry_date is not None and approval_date is not None:
            if expiry_date < approval_date:
                raise ValueError(
                    "Expiry date cannot be earlier than approval date"
                )

        return self.repository.update(
            organization_id=organization_id,
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

    def _validate_status(self, status: str):
        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "Invalid visa processing status"
            )
