from repositories.employer_dashboard import EmployerDashboardRepository
from services.authorization import AuthorizationContext, has_any_role


class EmployerDashboardService:
    def __init__(self, repository: EmployerDashboardRepository):
        self.repository = repository

    def get_dashboard(
        self,
        context: AuthorizationContext,
        employer_name: str,
    ):
        if not has_any_role(context, {"Employer Manager", "HR Manager", "Administrator"}):
            raise PermissionError("Required employer portal role")

        return self.repository.get_dashboard(
            context=context,
            employer_name=employer_name,
        )
