import base64
import json
from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient

import api.onboarding as onboarding_api

from main import app


ORGANIZATION_ID = "005F50D3-26AB-F111-9B32-000D3AC9134A"
APPLICATION_ID = "6528C71E-FEAD-F111-9B33-000D3AC8B575"
ONBOARDING_ID = "AD0E5641-E5B0-F111-9B33-000D3AC7AD82"

ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


def make_principal(
    principal_id,
    name,
    groups=None,
    roles=None,
):
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


def auth_headers():
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": "user-001",
        "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.test",
        "X-MS-CLIENT-PRINCIPAL": make_principal(
            "user-001",
            "Test Administrator",
            groups=[ADMINISTRATOR_GROUP_ID],
        ),
    }


def fake_organization_repository():
    return type(
        "FakeOrganizationRepository",
        (),
        {
            "get_active_memberships": lambda self, user_id: [
                type(
                    "Membership",
                    (),
                    {
                        "user_id": user_id,
                        "organization_id": ORGANIZATION_ID,
                        "status": "active",
                    },
                )()
            ]
        },
    )()


def fake_application_repository(application=None):
    return type(
        "FakeApplicationRepository",
        (),
        {
            "get_application": (
                lambda self, organization_id, application_id:
                application
            )
        },
    )()


def fake_onboarding(
    onboarding_id=ONBOARDING_ID,
    application_id=APPLICATION_ID,
):
    return SimpleNamespace(
        id=onboarding_id,
        application_id=application_id,
        employer_name="TBBD Test Employer",
        job_title="Recruitment Specialist",
        joining_date=date(2026, 10, 1),
        status="Pending",
        contract_signed=False,
        documents_verified=False,
        orientation_completed=False,
        accommodation_arranged=False,
        transport_arranged=False,
        notes="Initial onboarding record.",
        completed_at=None,
        created_at=None,
        updated_at=None,
    )


def test_onboarding_create_requires_authentication():
    client = TestClient(app)

    response = client.post(
        f"/api/onboarding?organization_id={ORGANIZATION_ID}",
        json={
            "application_id": APPLICATION_ID,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Authenticated user identity is required"
    )


def test_onboarding_create_rejects_missing_application_for_organization(
    monkeypatch,
):
    monkeypatch.setattr(
        onboarding_api,
        "_organization_repository",
        fake_organization_repository(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_application_repository",
        fake_application_repository(None),
    )

    client = TestClient(app)

    response = client.post(
        f"/api/onboarding?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
        json={
            "application_id": APPLICATION_ID,
            "employer_name": "TBBD Test Employer",
            "job_title": "Recruitment Specialist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Application not found for this organization"
    )


def test_onboarding_create_returns_created_record(
    monkeypatch,
):
    application = object()

    monkeypatch.setattr(
        onboarding_api,
        "_organization_repository",
        fake_organization_repository(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_application_repository",
        fake_application_repository(application),
    )

    created = fake_onboarding()

    monkeypatch.setattr(
        onboarding_api,
        "_onboarding_service",
        type(
            "FakeOnboardingService",
            (),
            {
                "create": lambda self, **kwargs: created,
            },
        )(),
    )

    client = TestClient(app)

    response = client.post(
        f"/api/onboarding?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
        json={
            "application_id": APPLICATION_ID,
            "employer_name": "TBBD Test Employer",
            "job_title": "Recruitment Specialist",
            "joining_date": "2026-10-01",
            "status": "Pending",
            "documents_verified": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["onboarding"]

    assert data["id"] == ONBOARDING_ID
    assert data["application_id"] == APPLICATION_ID
    assert data["employer_name"] == "TBBD Test Employer"
    assert data["status"] == "Pending"


def test_onboarding_list_requires_organization_owned_application(
    monkeypatch,
):
    monkeypatch.setattr(
        onboarding_api,
        "_organization_repository",
        fake_organization_repository(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_application_repository",
        fake_application_repository(None),
    )

    client = TestClient(app)

    response = client.get(
        f"/api/onboarding/application/{APPLICATION_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Application not found for this organization"
    )


def test_onboarding_list_by_application_returns_records(
    monkeypatch,
):
    application = object()
    records = [
        fake_onboarding(),
    ]

    monkeypatch.setattr(
        onboarding_api,
        "_organization_repository",
        fake_organization_repository(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_application_repository",
        fake_application_repository(application),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_onboarding_service",
        type(
            "FakeOnboardingService",
            (),
            {
                "list_by_application": (
                    lambda self, application_id: records
                ),
            },
        )(),
    )

    client = TestClient(app)

    response = client.get(
        f"/api/onboarding/application/{APPLICATION_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()["onboarding"]

    assert len(data) == 1
    assert data[0]["id"] == ONBOARDING_ID
    assert data[0]["application_id"] == APPLICATION_ID


def test_onboarding_get_rejects_record_from_other_organization(
    monkeypatch,
):
    application = None
    onboarding = fake_onboarding()

    monkeypatch.setattr(
        onboarding_api,
        "_organization_repository",
        fake_organization_repository(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_onboarding_service",
        type(
            "FakeOnboardingService",
            (),
            {
                "get": lambda self, onboarding_id: onboarding,
            },
        )(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_application_repository",
        fake_application_repository(application),
    )

    client = TestClient(app)

    response = client.get(
        f"/api/onboarding/{ONBOARDING_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Onboarding record not found"
    )


def test_onboarding_get_returns_record(
    monkeypatch,
):
    application = object()
    onboarding = fake_onboarding()

    monkeypatch.setattr(
        onboarding_api,
        "_organization_repository",
        fake_organization_repository(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_onboarding_service",
        type(
            "FakeOnboardingService",
            (),
            {
                "get": lambda self, onboarding_id: onboarding,
            },
        )(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_application_repository",
        fake_application_repository(application),
    )

    client = TestClient(app)

    response = client.get(
        f"/api/onboarding/{ONBOARDING_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()["onboarding"]

    assert data["id"] == ONBOARDING_ID
    assert data["application_id"] == APPLICATION_ID
    assert data["job_title"] == "Recruitment Specialist"


def test_onboarding_update_returns_updated_record(
    monkeypatch,
):
    application = object()
    onboarding = fake_onboarding()

    updated = fake_onboarding()
    updated.status = "Completed"
    updated.contract_signed = True
    updated.documents_verified = True
    updated.orientation_completed = True

    monkeypatch.setattr(
        onboarding_api,
        "_organization_repository",
        fake_organization_repository(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_onboarding_service",
        type(
            "FakeOnboardingService",
            (),
            {
                "get": lambda self, onboarding_id: onboarding,
                "update": lambda self, **kwargs: updated,
            },
        )(),
    )

    monkeypatch.setattr(
        onboarding_api,
        "_application_repository",
        fake_application_repository(application),
    )

    client = TestClient(app)

    response = client.put(
        f"/api/onboarding/{ONBOARDING_ID}"
        f"?organization_id={ORGANIZATION_ID}",
        headers=auth_headers(),
        json={
            "status": "Completed",
            "contract_signed": True,
            "documents_verified": True,
            "orientation_completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["onboarding"]

    assert data["id"] == ONBOARDING_ID
    assert data["status"] == "Completed"
    assert data["contract_signed"] is True
    assert data["documents_verified"] is True
    assert data["orientation_completed"] is True


def test_onboarding_service_rejects_invalid_status():
    from services.onboarding import OnboardingService

    class FakeRepository:
        def create(self, **kwargs):
            raise AssertionError(
                "Repository must not be called for invalid status"
            )

    service = OnboardingService(FakeRepository())

    try:
        service.create(
            application_id=APPLICATION_ID,
            status="Invalid Status",
        )
    except ValueError as exc:
        assert "Invalid onboarding status" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
