import base64
import json

from fastapi.testclient import TestClient

import api.visa_processing as visa_processing_api
from main import app


ORGANIZATION_ID = "005F50D3-26AB-F111-9B32-000D3AC9134A"
ADMINISTRATOR_GROUP_ID = "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66"


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


def test_visa_processing_create_requires_authentication():
    client = TestClient(app)

    response = client.post(
        f"/api/visa-processing?organization_id={ORGANIZATION_ID}",
        json={
            "application_id": "00000000-0000-0000-0000-000000000000",
            "test_type": "Practical Assessment",
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
        )(),
    )

    encoded_principal = make_principal(
        "user-001",
        "Test Administrator",
        groups=[ADMINISTRATOR_GROUP_ID],
    )

    client = TestClient(app)

    response = client.post(
        f"/api/visa-processing?organization_id={ORGANIZATION_ID}",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "user-001",
            "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.test",
            "X-MS-CLIENT-PRINCIPAL": encoded_principal,
        },
        json={
            "application_id": "00000000-0000-0000-0000-000000000000",
            "test_type": "Practical Assessment",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found for this organization"


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
        )(),
    )

    monkeypatch.setattr(
        visa_processing_api,
        "_application_repository",
        type(
            "FakeApplicationRepository",
            (),
            {
                "get_application": lambda self, organization_id, application_id: None
            },
        )(),
    )

    encoded_principal = make_principal(
        "user-001",
        "Test Administrator",
        groups=[ADMINISTRATOR_GROUP_ID],
    )

    client = TestClient(app)

    response = client.get(
        "/api/visa-processing/application/"
        "6528C71E-FEAD-F111-9B33-000D3AC8B575"
        f"?organization_id={ORGANIZATION_ID}",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "user-001",
            "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.test",
            "X-MS-CLIENT-PRINCIPAL": encoded_principal,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found for this organization"


def test_visa_processing_get_by_id_rejects_visa_processing_from_other_organization(
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
        )(),
    )

    monkeypatch.setattr(
        visa_processing_api,
        "_visa_processing_service",
        type(
            "FakeVisaProcessingService",
            (),
            {
                "get": lambda self, visa_processing_id: type(
                    "VisaProcessing",
                    (),
                    {
                        "id": visa_processing_id,
                        "application_id": "6528C71E-FEAD-F111-9B33-000D3AC8B575",
                    },
                )()
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
                "get_application": lambda self, organization_id, application_id: None
            },
        )(),
    )

    encoded_principal = make_principal(
        "user-001",
        "Test Administrator",
        groups=[ADMINISTRATOR_GROUP_ID],
    )

    client = TestClient(app)

    response = client.get(
        "/api/visa-processing/"
        "AD0E5641-E5B0-F111-9B33-000D3AC7AD82"
        f"?organization_id={ORGANIZATION_ID}",
        headers={
            "X-MS-CLIENT-PRINCIPAL-ID": "user-001",
            "X-MS-CLIENT-PRINCIPAL-NAME": "administrator@example.test",
            "X-MS-CLIENT-PRINCIPAL": encoded_principal,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trade test not found"


def test_visa_processing_service_calculates_result_and_completes_assessment():

    from services.visa_processing import VisaProcessingService

    class FakeRepository:
        def update_assessment(self, **kwargs):
            return kwargs

    service = VisaProcessingService(FakeRepository())

    result = service.update_assessment(
        visa_processing_id="trade-test-001",
        technical_knowledge_score=80,
        trade_skills_score=90,
        safety_awareness_score=70,
        tool_handling_score=80,
        communication_score=90,
        problem_solving_score=70,
        teamwork_score=80,
        assessment_notes="Assessment completed successfully.",
    )

    assert result["visa_processing_id"] == "trade-test-001"
    assert result["total_score"] == 80
    assert result["result"] == "Pass"
    assert result["status"] == "Completed"


def test_visa_processing_service_rejects_score_outside_valid_range():

    from services.visa_processing import VisaProcessingService

    class FakeRepository:
        def update_assessment(self, **kwargs):
            raise AssertionError(
                "Repository must not be called for invalid scores"
            )

    service = VisaProcessingService(FakeRepository())

    try:
        service.update_assessment(
            visa_processing_id="trade-test-001",
            technical_knowledge_score=101,
            trade_skills_score=90,
            safety_awareness_score=70,
            tool_handling_score=80,
            communication_score=90,
            problem_solving_score=70,
            teamwork_score=80,
        )
    except ValueError as exc:
        assert str(exc) == (
            "technical_knowledge_score must be between 0 and 100"
        )
    else:
        raise AssertionError("Expected ValueError")
