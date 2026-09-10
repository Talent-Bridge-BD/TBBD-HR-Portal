import base64
import json

from fastapi.testclient import TestClient

from main import app
from repositories.candidate import InMemoryCandidateRepository
from services.candidate import CandidateService
import api.candidate as candidate_api


candidate_api._repository = InMemoryCandidateRepository()
candidate_api._service = CandidateService(candidate_api._repository)

client = TestClient(app)

CANDIDATE_GROUP_ID = "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6"


def build_principal_header():
    principal = {
        "auth_typ": "aad",
        "claims": [
            {
                "typ": "http://schemas.microsoft.com/identity/claims/objectidentifier",
                "val": "test-principal-001",
            },
            {
                "typ": "groups",
                "val": CANDIDATE_GROUP_ID,
            },
            {
                "typ": "name",
                "val": "Test Candidate",
            },
            {
                "typ": "preferred_username",
                "val": "candidate@example.test",
            },
        ],
    }

    encoded = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")

    return encoded


def candidate_headers():
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": "test-principal-001",
        "X-MS-CLIENT-PRINCIPAL-NAME": "candidate@example.test",
        "X-MS-CLIENT-PRINCIPAL": build_principal_header(),
    }


def test_candidate_profile_requires_authenticated_identity():
    response = client.get("/api/candidate/profile")

    assert response.status_code == 401


def test_candidate_profile_can_be_created_and_retrieved():
    headers = candidate_headers()

    payload = {
        "first_name": "Test",
        "last_name": "Candidate",
        "email": "candidate@example.test",
        "professional_title": "Software Engineer",
    }

    response = client.put(
        "/api/candidate/profile",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["profile"]["user_id"] == "test-principal-001"

    response = client.get(
        "/api/candidate/profile",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["profile"]["first_name"] == "Test"
