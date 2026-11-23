import base64
import json

from fastapi.testclient import TestClient

import api.recruitment_pipeline as recruitment_api
from main import app
from models.organization import OrganizationMembership
from services.authorization import AuthorizationContext


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


def auth_headers(principal_id, principal):
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": principal_id,
        "X-MS-CLIENT-PRINCIPAL-NAME": "test@example.com",
        "X-MS-CLIENT-PRINCIPAL": principal,
    }


def pipeline_response():
    return {
        "Applied": 4,
        "Screening": 3,
        "Interview": 2,
        "Trade Test": 1,
        "Medical": 1,
        "Visa Processing": 0,
        "Ticketing": 0,
        "Onboarding": 0,
        "Deployment": 0,
        "Completed": 0,
    }


def test_recruitment_pipeline_requires_authentication():
    client = TestClient(app)

    response = client.get("/api/recruitment/pipeline")

    assert response.status_code == 401


def test_recruitment_pipeline_requires_principal_id(monkeypatch):
    principal = make_principal(
        "user-001",
        "Test User",
        roles=["HR Manager"],
    )

    monkeypatch.setattr(
        recruitment_api,
        "get_request_principal",
        lambda request: {
            "claims": [
                {"typ": "roles", "val": "HR Manager"},
            ]
        },
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers={
            "X-MS-CLIENT-PRINCIPAL": principal,
        },
    )

    assert response.status_code == 401


def test_employee_cannot_access_recruitment_pipeline(monkeypatch):
    principal = make_principal(
        "employee-001",
        "Test Employee",
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("employee-001", principal),
    )

    assert response.status_code == 403


def test_candidate_cannot_access_recruitment_pipeline(monkeypatch):
    principal = make_principal(
        "candidate-001",
        "Test Candidate",
        roles=["Candidate"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("candidate-001", principal),
    )

    assert response.status_code == 403


def test_hr_manager_can_access_recruitment_pipeline(monkeypatch):
    expected = pipeline_response()

    monkeypatch.setattr(
        recruitment_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: [
                        OrganizationMembership(
                            id="membership-001",
                            organization_id="org-001",
                            user_id=user_id,
                            role="HR Manager",
                            status="active",
                        )
                    ]
                )
            },
        )(),
    )

    monkeypatch.setattr(
        recruitment_api._repository,
        "get_pipeline_counts",
        lambda context: (
            expected
            if context.organization_ids == frozenset({"org-001"})
            else {}
        ),
    )

    principal = make_principal(
        "hr-001",
        "Test HR Manager",
        roles=["HR Manager"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("hr-001", principal),
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_employer_manager_can_access_recruitment_pipeline(monkeypatch):
    expected = pipeline_response()

    monkeypatch.setattr(
        recruitment_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: [
                        OrganizationMembership(
                            id="membership-001",
                            organization_id="org-001",
                            user_id=user_id,
                            role="Employer Manager",
                            status="active",
                        )
                    ]
                )
            },
        )(),
    )

    captured_context = {}

    def fake_get_pipeline_counts(context):
        captured_context["context"] = context
        return expected

    monkeypatch.setattr(
        recruitment_api._repository,
        "get_pipeline_counts",
        fake_get_pipeline_counts,
    )

    principal = make_principal(
        "employer-001",
        "Test Employer Manager",
        groups=["7088ce1f-8e01-4c7c-88fd-a257721a35df"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("employer-001", principal),
    )

    assert response.status_code == 200
    assert response.json() == expected
    assert captured_context["context"].organization_ids == frozenset(
        {"org-001"}
    )
    assert captured_context["context"].is_global_administrator is False


def test_administrator_can_access_recruitment_pipeline_without_membership(
    monkeypatch,
):
    expected = pipeline_response()

    monkeypatch.setattr(
        recruitment_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: []
                )
            },
        )(),
    )

    captured_context = {}

    def fake_get_pipeline_counts(context):
        captured_context["context"] = context
        return expected

    monkeypatch.setattr(
        recruitment_api._repository,
        "get_pipeline_counts",
        fake_get_pipeline_counts,
    )

    principal = make_principal(
        "admin-001",
        "Test Administrator",
        roles=["Administrator"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("admin-001", principal),
    )

    assert response.status_code == 200
    assert response.json() == expected
    assert captured_context["context"].organization_ids == frozenset()
    assert captured_context["context"].is_global_administrator is True


def test_hr_manager_without_memberships_gets_zero_pipeline(monkeypatch):
    expected = {
        "Applied": 0,
        "Screening": 0,
        "Interview": 0,
        "Trade Test": 0,
        "Medical": 0,
        "Visa Processing": 0,
        "Ticketing": 0,
        "Onboarding": 0,
        "Deployment": 0,
        "Completed": 0,
    }

    monkeypatch.setattr(
        recruitment_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: []
                )
            },
        )(),
    )

    monkeypatch.setattr(
        recruitment_api._repository,
        "get_pipeline_counts",
        lambda context: expected,
    )

    principal = make_principal(
        "hr-no-org-001",
        "HR Without Organization",
        roles=["HR Manager"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("hr-no-org-001", principal),
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_employer_manager_without_memberships_gets_zero_pipeline(monkeypatch):
    expected = {
        "Applied": 0,
        "Screening": 0,
        "Interview": 0,
        "Trade Test": 0,
        "Medical": 0,
        "Visa Processing": 0,
        "Ticketing": 0,
        "Onboarding": 0,
        "Deployment": 0,
        "Completed": 0,
    }

    monkeypatch.setattr(
        recruitment_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: []
                )
            },
        )(),
    )

    monkeypatch.setattr(
        recruitment_api._repository,
        "get_pipeline_counts",
        lambda context: expected,
    )

    principal = make_principal(
        "employer-no-org-001",
        "Employer Without Organization",
        roles=["Employer Manager"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("employer-no-org-001", principal),
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_recruitment_pipeline_preserves_exact_response_shape(monkeypatch):
    expected = pipeline_response()

    monkeypatch.setattr(
        recruitment_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": (
                    lambda self, user_id: []
                )
            },
        )(),
    )

    monkeypatch.setattr(
        recruitment_api._repository,
        "get_pipeline_counts",
        lambda context: expected,
    )

    principal = make_principal(
        "admin-shape-001",
        "Test Administrator",
        roles=["Administrator"],
    )

    client = TestClient(app)

    response = client.get(
        "/api/recruitment/pipeline",
        headers=auth_headers("admin-shape-001", principal),
    )

    assert response.status_code == 200
    assert set(response.json()) == {
        "Applied",
        "Screening",
        "Interview",
        "Trade Test",
        "Medical",
        "Visa Processing",
        "Ticketing",
        "Onboarding",
        "Deployment",
        "Completed",
    }


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed_sql = None
        self.parameters = None

    def execute(self, sql, parameters=()):
        self.executed_sql = sql
        self.parameters = parameters

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows):
        self.cursor_instance = FakeCursor(rows)

    def cursor(self):
        return self.cursor_instance

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_repository_returns_zero_for_no_organizations(monkeypatch):
    from repositories.recruitment_pipeline import RecruitmentPipelineRepository

    repository = RecruitmentPipelineRepository()

    context = AuthorizationContext(
        user_id="user-no-org",
        roles=frozenset({"Employer Manager"}),
        organization_ids=frozenset(),
        is_global_administrator=False,
    )

    connection_created = {"value": False}

    def unexpected_connection():
        connection_created["value"] = True
        raise AssertionError(
            "Database connection should not be opened for zero organizations"
        )

    monkeypatch.setattr(repository, "_connection", unexpected_connection)

    result = repository.get_pipeline_counts(context)

    assert result == {
        "Applied": 0,
        "Screening": 0,
        "Interview": 0,
        "Trade Test": 0,
        "Medical": 0,
        "Visa Processing": 0,
        "Ticketing": 0,
        "Onboarding": 0,
        "Deployment": 0,
        "Completed": 0,
    }
    assert connection_created["value"] is False


def test_repository_scopes_non_global_users_by_job_organization(monkeypatch):
    from repositories.recruitment_pipeline import RecruitmentPipelineRepository

    repository = RecruitmentPipelineRepository()

    rows = [
        type("Row", (), {"workflow_status": "Applied", "total": 2})(),
        type("Row", (), {"workflow_status": "Interview", "total": 1})(),
    ]

    connection = FakeConnection(rows)

    monkeypatch.setattr(
        repository,
        "_connection",
        lambda: connection,
    )

    context = AuthorizationContext(
        user_id="employer-001",
        roles=frozenset({"Employer Manager"}),
        organization_ids=frozenset({"org-001", "org-002"}),
        is_global_administrator=False,
    )

    result = repository.get_pipeline_counts(context)

    sql = connection.cursor_instance.executed_sql

    assert "dbo.candidates AS c" in sql
    assert "dbo.applications AS a" in sql
    assert "dbo.jobs AS j" in sql
    assert "a.candidate_id = c.id" in sql
    assert "j.id = a.job_id" in sql
    assert "j.organization_id IN (?, ?)" in sql
    assert "WHERE EXISTS" in sql

    assert set(connection.cursor_instance.parameters) == {
        "org-001",
        "org-002",
    }

    assert result["Applied"] == 2
    assert result["Interview"] == 1
    assert result["Screening"] == 0


def test_repository_uses_exists_to_prevent_duplicate_candidate_counts(
    monkeypatch,
):
    from repositories.recruitment_pipeline import RecruitmentPipelineRepository

    repository = RecruitmentPipelineRepository()

    rows = [
        type("Row", (), {"workflow_status": "Applied", "total": 3})(),
    ]

    connection = FakeConnection(rows)

    monkeypatch.setattr(
        repository,
        "_connection",
        lambda: connection,
    )

    context = AuthorizationContext(
        user_id="employer-001",
        roles=frozenset({"Employer Manager"}),
        organization_ids=frozenset({"org-001"}),
        is_global_administrator=False,
    )

    result = repository.get_pipeline_counts(context)

    sql = connection.cursor_instance.executed_sql

    assert "WHERE EXISTS" in sql
    assert "SELECT 1" in sql
    assert result["Applied"] == 3


def test_repository_global_administrator_does_not_require_organization_scope(
    monkeypatch,
):
    from repositories.recruitment_pipeline import RecruitmentPipelineRepository

    repository = RecruitmentPipelineRepository()

    rows = [
        type("Row", (), {"workflow_status": "Applied", "total": 7})(),
        type("Row", (), {"workflow_status": "Completed", "total": 2})(),
    ]

    connection = FakeConnection(rows)

    monkeypatch.setattr(
        repository,
        "_connection",
        lambda: connection,
    )

    context = AuthorizationContext(
        user_id="admin-001",
        roles=frozenset({"Administrator"}),
        organization_ids=frozenset(),
        is_global_administrator=True,
    )

    result = repository.get_pipeline_counts(context)

    sql = connection.cursor_instance.executed_sql

    assert "FROM dbo.candidates" in sql
    assert "GROUP BY workflow_status" in sql
    assert "WHERE EXISTS" not in sql
    assert connection.cursor_instance.parameters == ()

    assert result["Applied"] == 7
    assert result["Completed"] == 2
    assert result["Medical"] == 0


def test_repository_ignores_unknown_workflow_status(monkeypatch):
    from repositories.recruitment_pipeline import RecruitmentPipelineRepository

    repository = RecruitmentPipelineRepository()

    rows = [
        type("Row", (), {"workflow_status": "Applied", "total": 5})(),
        type("Row", (), {"workflow_status": "UnexpectedStatus", "total": 99})(),
    ]

    connection = FakeConnection(rows)

    monkeypatch.setattr(
        repository,
        "_connection",
        lambda: connection,
    )

    context = AuthorizationContext(
        user_id="admin-001",
        roles=frozenset({"Administrator"}),
        organization_ids=frozenset(),
        is_global_administrator=True,
    )

    result = repository.get_pipeline_counts(context)

    assert result["Applied"] == 5
    assert "UnexpectedStatus" not in result
