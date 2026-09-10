from repositories.onboarding import OnboardingRepository


class OnboardingService:

    def __init__(self, repository: OnboardingRepository):
        self.repository = repository

    def list_onboarding(
        self,
        organization_id: str,
    ):
        return self.repository.list_onboarding(
            organization_id,
        )

    def get_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
    ):
        return self.repository.get_onboarding(
            organization_id,
            onboarding_id,
        )

    def create_onboarding(
        self,
        organization_id: str,
        application_id: str,
        status: str,
        planned_start_date,
        employment_type: str | None,
        notes: str | None,
    ):
        return self.repository.create_onboarding(
            organization_id,
            application_id,
            status,
            planned_start_date,
            employment_type,
            notes,
        )

    def update_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
        status: str,
        planned_start_date,
        employment_type: str | None,
        notes: str | None,
    ):
        return self.repository.update_onboarding(
            organization_id,
            onboarding_id,
            status,
            planned_start_date,
            employment_type,
            notes,
        )

    def delete_onboarding(
        self,
        organization_id: str,
        onboarding_id: str,
    ):
        return self.repository.delete_onboarding(
            organization_id,
            onboarding_id,
        )
