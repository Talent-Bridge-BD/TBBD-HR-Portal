from models.employer_dashboard import (
    EmployerDashboard,
    EmployerDashboardStats,
    EmployerPipeline,
)
from repositories.employer_dashboard import SqlEmployerDashboardRepository
from services.authorization import AuthorizationContext


def test_sql_employer_dashboard_returns_zero_for_no_organizations():
    repository = SqlEmployerDashboardRepository()

    context = AuthorizationContext(
        user_id="user-without-org",
        roles=frozenset({"Employer Manager"}),
        organization_ids=frozenset(),
    )

    result = repository.get_dashboard(
        context=context,
        employer_name="Test Employer",
    )

    assert result.employer_name == "Test Employer"
    assert result.organization_name is None
    assert result.stats == EmployerDashboardStats(
        active_jobs=0,
        new_applications=0,
        candidates_pipeline=0,
        interviews_upcoming=0,
    )
    assert result.pipeline == EmployerPipeline(
        new=0,
        screening=0,
        shortlisted=0,
        interview=0,
        offer=0,
        hired=0,
    )
