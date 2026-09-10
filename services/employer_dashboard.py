from repositories.employer_dashboard import EmployerDashboardRepository
from services.authorization import AuthorizationContext, require_role


class EmployerDashboardService:
    def __init__(self, repository: EmployerDashboardRepository):
        self.repository = repository

    def get_dashboard(
        self,
        context: AuthorizationContext,
        employer_name: str,
    ):
        require_role(context, "Employer Manager")

        return self.repository.get_dashboard(
            context=context,
            employer_name=employer_name,
        )
