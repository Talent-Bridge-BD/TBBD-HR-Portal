from repositories.screening import SqlScreeningRepository


class ScreeningService:

    def __init__(
        self,
        repository: SqlScreeningRepository,
    ):
        self.repository = repository

    def get_by_application(
        self,
        application_id: str,
    ):
        return self.repository.get_by_application(
            application_id,
        )

    def save(
        self,
        application_id: str,
        basic_eligibility: str | None = None,
        relevant_experience: str | None = None,
        education: str | None = None,
        communication: str | None = None,
        availability: str | None = None,
        screening_notes: str | None = None,
        recommendation: str | None = None,
    ):
        existing = self.repository.get_by_application(
            application_id,
        )

        if existing is None:
            return self.repository.create(
                application_id=application_id,
                basic_eligibility=basic_eligibility,
                relevant_experience=relevant_experience,
                education=education,
                communication=communication,
                availability=availability,
                screening_notes=screening_notes,
                recommendation=recommendation,
            )

        return self.repository.update(
            screening_id=existing.id,
            basic_eligibility=basic_eligibility,
            relevant_experience=relevant_experience,
            education=education,
            communication=communication,
            availability=availability,
            screening_notes=screening_notes,
            recommendation=recommendation,
        )
