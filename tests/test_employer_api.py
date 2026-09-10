import base64
import json

from fastapi.testclient import TestClient

import api.employer as employer_api
from main import app
from models.employer_dashboard import (
    EmployerDashboard,
    EmployerDashboardStats,
    EmployerPipeline,
)
from repositories.employer_dashboard import InMemoryEmployerDashboardRepository
from services.employer_dashboard import EmployerDashboardService


def make_principal(principal_id, name, groups=None, roles=None):
    principal = {
        "claims": [
            {"typ": "name", "val": name},
            *[
                {"typ": "groups", "val": group}
                for group in (groups or [])
            ],
            *[
                {"typ": "roles", "val": role}
                for role in (roles or [])
            ],
        ]
    }

    return base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")


def test_employer_dashboard_requires_authentication():
    client = TestClient(app)

    response = client.get("/api/employer/dashboard")

    assert response.status_code == 401


def test_employer_manager_can_access_dashboard(monkeypatch):
    dashboard = EmployerDashboard(
        employer_name="Test Employer",
        organization_name="Test Organization",
        stats=EmployerDashboardStats(3, 5, 12, 2),
        pipeline=EmployerPipeline(5, 3, 2, 1, 1, 0),
    )

    repository = InMemoryEmployerDashboardRepository(dashboard)

    monkeypatch.setattr(
        employer_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": lambda self, user_id: []
            },
        )(),
    )

    monkeypatch.setattr(
        employer_api,
        "_service",
        EmployerDashboardService(repository),
    )

    encoded_principal = make_principal(
        "user-001",
        "Test Employer",
        groups=["7088ce1f-8e01-4c7c-88fd-a257721a35df"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/employer/dashboard",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "user-001",
            "X-MS-CLIENT-PRINCIPAL-NAME": "employer@example.com",
            "X-MS-CLIENT-PRINCIPAL": encoded_principal,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["employer_name"] == "Test Employer"
    assert data["organization_name"] == "Test Organization"
    assert data["stats"]["active_jobs"] == 3
    assert data["stats"]["new_applications"] == 5
    assert data["pipeline"]["shortlisted"] == 2


def test_employee_cannot_access_employer_dashboard(monkeypatch):
    dashboard = EmployerDashboard(
        employer_name="Test Employer",
        organization_name="Test Organization",
        stats=EmployerDashboardStats(3, 5, 12, 2),
        pipeline=EmployerPipeline(5, 3, 2, 1, 1, 0),
    )

    repository = InMemoryEmployerDashboardRepository(dashboard)

    monkeypatch.setattr(
        employer_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": lambda self, user_id: []
            },
        )(),
    )

    monkeypatch.setattr(
        employer_api,
        "_service",
        EmployerDashboardService(repository),
    )

    encoded_principal = make_principal(
        "user-002",
        "Test Employee",
    )

    client = TestClient(app)

    response = client.get(
        "/api/employer/dashboard",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "user-002",
            "X-MS-CLIENT-PRINCIPAL-NAME": "employee@example.com",
            "X-MS-CLIENT-PRINCIPAL": encoded_principal,
        },
    )

    assert response.status_code == 403
