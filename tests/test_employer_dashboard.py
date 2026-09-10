from models.employer_dashboard import (
    EmployerDashboard,
    EmployerDashboardStats,
    EmployerPipeline,
)
from repositories.employer_dashboard import (
    InMemoryEmployerDashboardRepository,
)
from services.authorization import AuthorizationContext


def test_employer_dashboard_repository_returns_dashboard():
    dashboard = EmployerDashboard(
        employer_name="Test Employer",
        organization_name="Test Organization",
        stats=EmployerDashboardStats(
            active_jobs=3,
            new_applications=5,
            candidates_pipeline=12,
            interviews_upcoming=2,
        ),
        pipeline=EmployerPipeline(
            new=5,
            screening=3,
            shortlisted=2,
            interview=1,
            offer=1,
            hired=0,
        ),
    )

    repository = InMemoryEmployerDashboardRepository(dashboard)

    context = AuthorizationContext(
        user_id="user-001",
        roles=frozenset({"Employer Manager"}),
        organization_ids=frozenset({"org-001"}),
    )

    result = repository.get_dashboard(
        context=context,
        employer_name="Test Employer",
    )

    assert result.employer_name == "Test Employer"
    assert result.organization_name == "Test Organization"
    assert result.stats.active_jobs == 3
    assert result.stats.new_applications == 5
    assert result.stats.candidates_pipeline == 12
    assert result.stats.interviews_upcoming == 2
    assert result.pipeline.new == 5
    assert result.pipeline.screening == 3
    assert result.pipeline.shortlisted == 2
    assert result.pipeline.interview == 1
    assert result.pipeline.offer == 1
    assert result.pipeline.hired == 0
