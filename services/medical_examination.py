from repositories.medical_examination import SqlMedicalExaminationRepository


class MedicalExaminationService:

    VALID_STATUSES = {
        "Scheduled",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    VALID_RESULTS = {
        "Pending",
        "Fit",
        "Unfit",
        "Further Review",
    }

    def __init__(
        self,
        repository: SqlMedicalExaminationRepository,
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
        medical_center: str | None = None,
        examination_date=None,
        doctor_name: str | None = None,
        medical_type: str | None = None,
    ):
        return self.repository.create(
            organization_id=organization_id,
            application_id=application_id,
            medical_center=medical_center,
            examination_date=examination_date,
            doctor_name=doctor_name,
            medical_type=medical_type,
        )

    def get(
        self,
        organization_id: str,
        medical_examination_id: str,
    ):
        return self.repository.get(
            organization_id,
            medical_examination_id,
        )

    def update_assessment(
        self,
        organization_id: str,
        medical_examination_id: str,
        medical_center: str | None,
        examination_date,
        doctor_name: str | None,
        medical_type: str | None,
        status: str,
        result: str,
        report_notes: str | None = None,
        completed_at=None,
    ):
        if status not in self.VALID_STATUSES:
            raise ValueError(
                "Invalid medical examination status"
            )

        if result not in self.VALID_RESULTS:
            raise ValueError(
                "Invalid medical examination result"
            )

        if status == "Completed" and completed_at is None:
            from datetime import datetime, timezone

            completed_at = datetime.now(timezone.utc)

        if status != "Completed":
            completed_at = None

        return self.repository.update_assessment(
            organization_id=organization_id,
            medical_examination_id=medical_examination_id,
            medical_center=medical_center,
            examination_date=examination_date,
            doctor_name=doctor_name,
            medical_type=medical_type,
            status=status,
            result=result,
            report_notes=report_notes,
            completed_at=completed_at,
        )
