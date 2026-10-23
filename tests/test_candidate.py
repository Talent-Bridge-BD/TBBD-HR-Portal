import base64
import json
import os

from fastapi.testclient import TestClient

from main import app
from api import candidate as candidate_api
from repositories.application_roles import InMemoryApplicationRoleRepository
from repositories.candidate import InMemoryCandidateRepository
from repositories.candidate_approvals import InMemoryCandidateApprovalRepository
from services.candidate import CandidateService


candidate_api._repository = InMemoryCandidateRepository()
candidate_api._service = CandidateService(candidate_api._repository)
candidate_api._approval_repository = InMemoryCandidateApprovalRepository()
candidate_api._application_role_repository = InMemoryApplicationRoleRepository()


def grant_candidate_role(user_id):
    candidate_api._application_role_repository.grant_role(
        user_id,
        "Candidate",
        assigned_by="test-admin",
    )


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
    approval = candidate_api._approval_repository.ensure_candidate(
        "test-principal-001"
    )
    if approval["approval_status"] == "pending":
        candidate_api._approval_repository.review_candidate(
            "test-principal-001",
            status="approved",
            reviewed_by="test-admin",
            approval_notes="Approved test fixture",
        )
    grant_candidate_role("test-principal-001")
    return {
        "X-MS-CLIENT-PRINCIPAL-ID": "test-principal-001",
        "X-MS-CLIENT-PRINCIPAL-NAME": "candidate@example.test",
        "X-MS-CLIENT-PRINCIPAL": build_principal_header(),
    }


def test_candidate_profile_requires_authenticated_identity():
    original_local_auth = os.environ.get("TBBD_LOCAL_AUTH")
    os.environ["TBBD_LOCAL_AUTH"] = "0"
    try:
        response = client.get("/api/candidate/profile")
    finally:
        if original_local_auth is None:
            os.environ.pop("TBBD_LOCAL_AUTH", None)
        else:
            os.environ["TBBD_LOCAL_AUTH"] = original_local_auth
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


def test_external_id_candidate_can_create_profile_without_workforce_group():
    headers = candidate_headers()
    principal = json.loads(
        base64.b64decode(headers["X-MS-CLIENT-PRINCIPAL"])
    )
    principal["claims"] = [
        claim for claim in principal["claims"]
        if not (
            claim.get("typ") == "groups"
            and claim.get("val") == CANDIDATE_GROUP_ID
        )
    ]
    principal["claims"].append({"typ": "tid", "val": "c8573333-aad0-4a28-8e40-c20e17989f61"})
    principal["provider_name"] = "TBBDCandidateExternalID"

    headers["X-MS-CLIENT-PRINCIPAL-ID"] = "external-candidate-test-001"
    grant_candidate_role("external-candidate-test-001")
    candidate_api._approval_repository.ensure_candidate(
        "external-candidate-test-001"
    )
    candidate_api._approval_repository.review_candidate(
        "external-candidate-test-001",
        status="approved",
        reviewed_by="test-admin",
        approval_notes="Approved external identity test",
    )
    headers["X-MS-CLIENT-PRINCIPAL-NAME"] = "external.candidate@example.test"
    headers["X-MS-CLIENT-PRINCIPAL"] = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")

    response = client.put(
        "/api/candidate/profile",
        headers=headers,
        json={
            "first_name": "External",
            "last_name": "Candidate",
            "email": "external.candidate@example.test",
            "professional_title": "Job Applicant",
        },
    )
    assert response.status_code == 200
    assert response.json()["profile"]["user_id"] == "external-candidate-test-001"


def test_pending_candidate_can_check_approval_status():
    candidate_api._approval_repository = InMemoryCandidateApprovalRepository()
    headers = candidate_headers()
    principal = __import__("json").loads(
        __import__("base64").b64decode(headers["X-MS-CLIENT-PRINCIPAL"])
    )
    headers["X-MS-CLIENT-PRINCIPAL-ID"] = "pending-status-test"
    grant_candidate_role("pending-status-test")
    principal["provider_name"] = "TBBDCandidateExternalID"
    headers["X-MS-CLIENT-PRINCIPAL"] = __import__("base64").b64encode(
        __import__("json").dumps(principal).encode("utf-8")
    ).decode("utf-8")

    response = client.get(
        "/api/candidate/approval-status",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["approval_status"] == "pending"


def test_pending_candidate_can_save_and_resume_profile():
    candidate_api._approval_repository = InMemoryCandidateApprovalRepository()
    headers = candidate_headers()
    principal = json.loads(
        base64.b64decode(headers["X-MS-CLIENT-PRINCIPAL"])
    )
    headers["X-MS-CLIENT-PRINCIPAL-ID"] = "pending-profile-resume-test"
    grant_candidate_role("pending-profile-resume-test")
    principal["provider_name"] = "TBBDCandidateExternalID"
    headers["X-MS-CLIENT-PRINCIPAL"] = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "first_name": "Pending",
        "last_name": "Candidate",
        "email": "pending.candidate@example.test",
        "professional_title": "Profile in progress",
    }

    saved = client.put(
        "/api/candidate/profile",
        headers=headers,
        json=payload,
    )
    assert saved.status_code == 200
    assert saved.json()["profile"]["first_name"] == "Pending"

    # A later sign-in uses the same identity and retrieves the saved progress.
    reopened = client.get("/api/candidate/profile", headers=headers)
    assert reopened.status_code == 200
    assert reopened.json()["profile"]["first_name"] == "Pending"
    assert reopened.json()["profile"]["professional_title"] == "Profile in progress"


def test_pending_candidate_still_cannot_access_jobs():
    candidate_api._approval_repository = InMemoryCandidateApprovalRepository()
    headers = candidate_headers()
    principal = json.loads(
        base64.b64decode(headers["X-MS-CLIENT-PRINCIPAL"])
    )
    headers["X-MS-CLIENT-PRINCIPAL-ID"] = "pending-jobs-block-test"
    grant_candidate_role("pending-jobs-block-test")
    principal["provider_name"] = "TBBDCandidateExternalID"
    headers["X-MS-CLIENT-PRINCIPAL"] = base64.b64encode(
        json.dumps(principal).encode("utf-8")
    ).decode("utf-8")

    response = client.get("/api/candidate/jobs", headers=headers)
    assert response.status_code == 403
