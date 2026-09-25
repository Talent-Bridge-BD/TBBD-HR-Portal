import pytest

from models.employer_dashboard import (
    EmployerDashboard,
    EmployerDashboardStats,
    EmployerPipeline,
)
from repositories.employer_dashboard import InMemoryEmployerDashboardRepository
from services.authorization import AuthorizationContext
from services.employer_dashboard import EmployerDashboardService


def test_employer_manager_can_access_dashboard():
    dashboard = EmployerDashboard(
        employer_name="Test Employer",
        organization_name="Test Organization",
        stats=EmployerDashboardStats(3, 5, 12, 2),
        pipeline=EmployerPipeline(
        5, 3, 1, 0, 0, 0, 0, 0, 0, 0
    ),
    )

    repository = InMemoryEmployerDashboardRepository(dashboard)
    service = EmployerDashboardService(repository)

    context = AuthorizationContext(
        user_id="user-001",
        roles=frozenset({"Employer Manager"}),
        organization_ids=frozenset({"org-001"}),
        is_global_administrator=False,
    )

    result = service.get_dashboard(context, "Test Employer")

    assert result.stats.active_jobs == 3


@pytest.mark.parametrize(
    "role",
    ["HR Manager", "Administrator"],
)
def test_hr_manager_and_administrator_can_access_dashboard(role):
    dashboard = EmployerDashboard(
        employer_name="Test Employer",
        organization_name="Test Organization",
        stats=EmployerDashboardStats(3, 5, 12, 2),
        pipeline=EmployerPipeline(
        5, 3, 1, 0, 0, 0, 0, 0, 0, 0
    ),
    )
    repository = InMemoryEmployerDashboardRepository(dashboard)
    service = EmployerDashboardService(repository)
    context = AuthorizationContext(
        user_id="user-003",
        roles=frozenset({role}),
        organization_ids=frozenset({"org-001"}),
        is_global_administrator=(role == "Administrator"),
    )

    result = service.get_dashboard(context, "Test Employer")

    assert result.stats.active_jobs == 3


def test_non_employer_manager_cannot_access_dashboard():
    dashboard = EmployerDashboard(
        employer_name="Test Employer",
        organization_name="Test Organization",
        stats=EmployerDashboardStats(3, 5, 12, 2),
        pipeline=EmployerPipeline(
        5, 3, 1, 0, 0, 0, 0, 0, 0, 0
    ),
    )

    repository = InMemoryEmployerDashboardRepository(dashboard)
    service = EmployerDashboardService(repository)

    context = AuthorizationContext(
        user_id="user-002",
        roles=frozenset({"Employee"}),
        organization_ids=frozenset({"org-001"}),
        is_global_administrator=False,
    )

    with pytest.raises(PermissionError):
        service.get_dashboard(context, "Test Employer")
