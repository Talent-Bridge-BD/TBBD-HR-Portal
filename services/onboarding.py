from repositories.onboarding import SqlOnboardingRepository


class OnboardingService:

    ALLOWED_STATUSES = {
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    def __init__(
        self,
        repository: SqlOnboardingRepository,
    ):
        self.repository = repository

    def list_by_application(
        self,
        application_id: str,
    ):
        return self.repository.list_by_application(
            application_id,
        )

    def create(
        self,
        application_id: str,
        employer_name: str | None = None,
        job_title: str | None = None,
        joining_date=None,
        status: str = "Pending",
        contract_signed: bool = False,
        documents_verified: bool = False,
        orientation_completed: bool = False,
        accommodation_arranged: bool = False,
        transport_arranged: bool = False,
        notes: str | None = None,
    ):
        self._validate_status(status)

        return self.repository.create(
            application_id=application_id,
            employer_name=employer_name,
            job_title=job_title,
            joining_date=joining_date,
            status=status,
            contract_signed=contract_signed,
            documents_verified=documents_verified,
            orientation_completed=orientation_completed,
            accommodation_arranged=accommodation_arranged,
            transport_arranged=transport_arranged,
            notes=notes,
        )

    def get(
        self,
        onboarding_id: str,
    ):
        return self.repository.get(
            onboarding_id,
        )

    def update(
        self,
        onboarding_id: str,
        employer_name: str | None = None,
        job_title: str | None = None,
        joining_date=None,
        status: str | None = None,
        contract_signed: bool | None = None,
        documents_verified: bool | None = None,
        orientation_completed: bool | None = None,
        accommodation_arranged: bool | None = None,
        transport_arranged: bool | None = None,
        notes: str | None = None,
        completed_at=None,
    ):
        if status is not None:
            self._validate_status(status)

        return self.repository.update(
            onboarding_id=onboarding_id,
            employer_name=employer_name,
            job_title=job_title,
            joining_date=joining_date,
            status=status,
            contract_signed=contract_signed,
            documents_verified=documents_verified,
            orientation_completed=orientation_completed,
            accommodation_arranged=accommodation_arranged,
            transport_arranged=transport_arranged,
            notes=notes,
            completed_at=completed_at,
        )

    @classmethod
    def _validate_status(cls, status: str):
        if status not in cls.ALLOWED_STATUSES:
            allowed = ", ".join(sorted(cls.ALLOWED_STATUSES))
            raise ValueError(
                f"Invalid onboarding status '{status}'. "
                f"Allowed statuses: {allowed}"
            )
