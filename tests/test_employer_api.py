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
from services.local_auth import TBBD_EMPLOYER_EXTERNAL_ID_CLIENT_ID


def make_principal(
    principal_id, name, groups=None, roles=None, tenant_id=None, audience=None, object_id=None
):
    claims = [
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
    if tenant_id:
        claims.append({"typ": "tid", "val": tenant_id})
    if audience:
        claims.append({"typ": "aud", "val": audience})
    if tenant_id:
        claims.append({"typ": "oid", "val": object_id or principal_id})
    principal = {"claims": claims}

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
        pipeline=EmployerPipeline(5, 3, 1, 0, 0, 0, 0, 0, 0, 0),
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
    assert data["pipeline"]["applied"] == 5
    assert data["pipeline"]["screening"] == 3
    assert data["pipeline"]["interview"] == 1
    assert data["pipeline"]["trade_test"] == 0
    assert data["pipeline"]["medical"] == 0
    assert data["pipeline"]["visa_processing"] == 0
    assert data["pipeline"]["ticketing"] == 0
    assert data["pipeline"]["onboarding"] == 0
    assert data["pipeline"]["deployment"] == 0
    assert data["pipeline"]["completed"] == 0

def test_employee_cannot_access_employer_dashboard(monkeypatch):
    dashboard = EmployerDashboard(
        employer_name="Test Employer",
        organization_name="Test Organization",
        stats=EmployerDashboardStats(3, 5, 12, 2),
        pipeline=EmployerPipeline(5, 3, 1, 0, 0, 0, 0, 0, 0, 0),
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


def test_employer_external_identity_uses_mapped_application_user_and_membership(monkeypatch):
    from types import SimpleNamespace

    dashboard = EmployerDashboard(
        employer_name="Existing Employer",
        organization_name="Existing Organization",
        stats=EmployerDashboardStats(3, 5, 12, 2),
        pipeline=EmployerPipeline(5, 3, 1, 0, 0, 0, 0, 0, 0, 0),
    )
    monkeypatch.setattr(
        employer_api, "_service", EmployerDashboardService(
            InMemoryEmployerDashboardRepository(dashboard)
        ),
    )
    lookups = []
    monkeypatch.setattr(
        employer_api, "_identity_mapping_repository",
        type("FakeMappingRepository", (), {
            "get_mapping": lambda self, **kwargs: {
                "id": "mapping-001",
                "application_user_id": "canonical-existing-user",
                "status": "Active",
            }
        })(),
    )
    monkeypatch.setattr(
        employer_api, "_organization_repository",
        type("FakeOrganizationRepository", (), {
            "get_active_memberships": lambda self, user_id: (
                lookups.append(user_id) or [
                    SimpleNamespace(
                        user_id=user_id,
                        organization_id="existing-org",
                        role="Employer Manager",
                        status="active",
                    )
                ]
            )
        })(),
    )

    encoded = make_principal(
        "new-employer-external-object-id",
        "Existing Employer",
        tenant_id=employer_api.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        audience=TBBD_EMPLOYER_EXTERNAL_ID_CLIENT_ID,
    )
    response = TestClient(app).get(
        "/api/employer/dashboard",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "new-employer-external-object-id",
            "X-MS-CLIENT-PRINCIPAL": encoded,
        },
    )

    assert response.status_code == 200, response.text
    assert lookups == ["canonical-existing-user"]


def test_employer_external_identity_rejects_wrong_audience(monkeypatch):
    encoded = make_principal(
        "external-object-id",
        "Employer",
        tenant_id=employer_api.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        audience="wrong-client-id",
    )
    response = TestClient(app).get(
        "/api/employer/dashboard",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "external-object-id",
            "X-MS-CLIENT-PRINCIPAL": encoded,
        },
    )
    assert response.status_code == 401


def test_employer_external_identity_requires_active_employer_manager_membership(monkeypatch):
    encoded = make_principal(
        "external-object-id",
        "Employer",
        tenant_id=employer_api.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        audience=TBBD_EMPLOYER_EXTERNAL_ID_CLIENT_ID,
    )
    monkeypatch.setattr(
        employer_api, "_identity_mapping_repository",
        type("FakeMappingRepository", (), {"get_mapping": lambda self, **kwargs: None})(),
    )
    monkeypatch.setattr(
        employer_api, "_organization_repository",
        type("FakeOrganizationRepository", (), {"get_active_memberships": lambda self, user_id: []})(),
    )
    response = TestClient(app).get(
        "/api/employer/dashboard",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "external-object-id",
            "X-MS-CLIENT-PRINCIPAL": encoded,
        },
    )
    assert response.status_code == 403


def test_unmapped_employer_external_identity_cannot_use_external_id_membership(
    monkeypatch,
):
    from types import SimpleNamespace

    external_object_id = "unmapped-employer-external-object-id"
    membership_lookups = []

    encoded = make_principal(
        external_object_id,
        "Unmapped Employer",
        tenant_id=employer_api.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        audience=TBBD_EMPLOYER_EXTERNAL_ID_CLIENT_ID,
    )

    monkeypatch.setattr(
        employer_api,
        "_identity_mapping_repository",
        type(
            "FakeMappingRepository",
            (),
            {"get_mapping": lambda self, **kwargs: None},
        )(),
    )

    def get_memberships(self, user_id):
        membership_lookups.append(user_id)
        return [
            SimpleNamespace(
                user_id=user_id,
                organization_id="existing-org",
                role="Employer Manager",
                status="active",
            )
        ]

    monkeypatch.setattr(
        employer_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {"get_active_memberships": get_memberships},
        )(),
    )

    response = TestClient(app).get(
        "/api/employer/dashboard",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": external_object_id,
            "X-MS-CLIENT-PRINCIPAL": encoded,
        },
    )

    assert response.status_code == 403
    assert membership_lookups == []


def test_employer_external_identity_rejects_revoked_mapping(monkeypatch):
    encoded = make_principal(
        "external-object-id",
        "Employer",
        tenant_id=employer_api.TBBD_EMPLOYER_EXTERNAL_ID_TENANT_ID,
        audience=TBBD_EMPLOYER_EXTERNAL_ID_CLIENT_ID,
    )
    monkeypatch.setattr(
        employer_api, "_identity_mapping_repository",
        type("FakeMappingRepository", (), {
            "get_mapping": lambda self, **kwargs: {
                "application_user_id": "canonical-existing-user",
                "status": "Revoked",
            }
        })(),
    )
    response = TestClient(app).get(
        "/api/employer/dashboard",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "external-object-id",
            "X-MS-CLIENT-PRINCIPAL": encoded,
        },
    )
    assert response.status_code == 403
