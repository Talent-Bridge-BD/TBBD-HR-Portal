import base64
import json

from fastapi.testclient import TestClient

import api.visa_processing as visa_processing_api
from main import app


ORGANIZATION_ID = "005F50D3-26AB-F111-9B32-000D3AC9134A"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c7c-88fd-aeba636a8a66"


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


def authenticated_headers():
    encoded_principal = make_principal(
        "user-001",
        "Test Administrator",
        groups=[ADMINISTRATOR_GROUP_ID],
    )

    return {
        "X-MS-CLIENT-PRINCIPAL-ID": "user-001",
        "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.test",
        "X-MS-CLIENT-PRINCIPAL": encoded_principal,
    }


def fake_active_membership():
    return type(
        "Membership",
        (),
        {
            "user_id": "user-001",
            "organization_id": ORGANIZATION_ID,
            "status": "active",
        },
    )()


def test_visa_processing_create_requires_authentication():
    client = TestClient(app)

    response = client.post(
        f"/api/visa-processing?organization_id={ORGANIZATION_ID}",
        json={
            "application_id": "00000000-0000-0000-0000-000000000000",
            "visa_type": "Employment Visa",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authenticated user identity is required"


def test_visa_processing_create_rejects_missing_application_for_organization(
    monkeypatch,
):
    monkeypatch.setattr(
        visa_processing_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": lambda self, user_id: [
                    fake_active_membership()
                ]
            },
        )(),
    )

    monkeypatch.setattr(
        visa_processing_api,
        "_application_repository",
        type(
            "FakeApplicationRepository",
            (),
            {
                "get_application": lambda self, organization_id, application_id: None,
                    "get_application_by_id": lambda self, application_id: None
            },
        )(),
    )

    client = TestClient(app)

    response = client.post(
        f"/api/visa-processing?organization_id={ORGANIZATION_ID}",
        headers=authenticated_headers(),
        json={
            "application_id": "00000000-0000-0000-0000-000000000000",
            "visa_type": "Employment Visa",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_visa_processing_get_by_application_requires_organization_owned_application(
    monkeypatch,
):
    monkeypatch.setattr(
        visa_processing_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": lambda self, user_id: [
                    fake_active_membership()
                ]
            },
        )(),
    )

    monkeypatch.setattr(
        visa_processing_api,
        "_application_repository",
        type(
            "FakeApplicationRepository",
            (),
            {
                "get_application": lambda self, organization_id, application_id: None,
                    "get_application_by_id": lambda self, application_id: None
            },
        )(),
    )

    client = TestClient(app)

    response = client.get(
        "/api/visa-processing/application/"
        "6528C71E-FEAD-F111-9B33-000D3AC8B575"
        f"?organization_id={ORGANIZATION_ID}",
        headers=authenticated_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_visa_processing_get_by_id_rejects_record_from_other_organization(
    monkeypatch,
):
    monkeypatch.setattr(
        visa_processing_api,
        "_organization_repository",
        type(
            "FakeOrganizationRepository",
            (),
            {
                "get_active_memberships": lambda self, user_id: [
                    fake_active_membership()
                ]
            },
        )(),
    )

    monkeypatch.setattr(
        visa_processing_api,
        "_visa_processing_service",
        type(
            "FakeVisaProcessingService",
            (),
            {
                "get": lambda self, visa_processing_id, organization_id=None: None
            },
        )(),
    )

    client = TestClient(app)

    response = client.get(
        "/api/visa-processing/"
        "AD0E5641-E5B0-F111-9B33-000D3AC7AD82"
        f"?organization_id={ORGANIZATION_ID}",
        headers=authenticated_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Visa processing record not found"


def test_visa_processing_service_rejects_invalid_status():
    from services.visa_processing import VisaProcessingService

    class FakeRepository:
        def update(self, **kwargs):
            raise AssertionError(
                "Repository must not be called for invalid status"
            )

    service = VisaProcessingService(FakeRepository())

    try:
        service.update(
            visa_processing_id="visa-processing-001",
            status="UnknownStatus",
        )
    except ValueError as exc:
        assert str(exc).startswith(
            "Invalid visa processing status."
        )
    else:
        raise AssertionError("Expected ValueError")


def test_visa_processing_service_accepts_valid_status():
    from services.visa_processing import VisaProcessingService

    expected = {
        "id": "visa-processing-001",
        "application_id": "application-001",
        "status": "Processing",
    }

    class FakeRepository:
        def update(self, **kwargs):
            assert kwargs["visa_processing_id"] == "visa-processing-001"
            assert kwargs["status"] == "Processing"

            return type(
                "VisaProcessing",
                (),
                expected,
            )()

    service = VisaProcessingService(FakeRepository())

    result = service.update(
        visa_processing_id="visa-processing-001",
        status="Processing",
    )

    assert result.id == "visa-processing-001"
    assert result.application_id == "application-001"
    assert result.status == "Processing"


def test_visa_processing_service_create_passes_real_fields_to_repository():
    from services.visa_processing import VisaProcessingService

    expected = {
        "id": "visa-processing-001",
        "application_id": "application-001",
        "visa_type": "Employment Visa",
        "visa_number": "VISA-12345",
        "application_number": "APP-12345",
        "submission_date": None,
        "approval_date": None,
        "expiry_date": None,
        "status": "Pending",
        "sponsor_name": "Talent Bridge BD",
        "sponsor_reference": "TBBD-REF-001",
        "notes": "Initial visa processing record.",
    }

    class FakeRepository:
        def create(self, **kwargs):
            assert kwargs["application_id"] == "application-001"
            assert kwargs["visa_type"] == "Employment Visa"
            assert kwargs["visa_number"] == "VISA-12345"
            assert kwargs["application_number"] == "APP-12345"
            assert kwargs["status"] == "Pending"
            assert kwargs["sponsor_name"] == "Talent Bridge BD"
            assert kwargs["sponsor_reference"] == "TBBD-REF-001"
            assert kwargs["notes"] == "Initial visa processing record."

            return type(
                "VisaProcessing",
                (),
                expected,
            )()

    service = VisaProcessingService(FakeRepository())

    result = service.create(
        application_id="application-001",
        visa_type="Employment Visa",
        visa_number="VISA-12345",
        application_number="APP-12345",
        status="Pending",
        sponsor_name="Talent Bridge BD",
        sponsor_reference="TBBD-REF-001",
        notes="Initial visa processing record.",
    )

    assert result.id == "visa-processing-001"
    assert result.application_id == "application-001"
    assert result.visa_type == "Employment Visa"
    assert result.visa_number == "VISA-12345"
    assert result.application_number == "APP-12345"
    assert result.status == "Pending"
    assert result.sponsor_name == "Talent Bridge BD"
    assert result.sponsor_reference == "TBBD-REF-001"
    assert result.notes == "Initial visa processing record."
