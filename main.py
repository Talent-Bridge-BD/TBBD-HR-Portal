import os
from pathlib import Path

import requests
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from services.authorization import build_authorization_context
from services.local_auth import get_request_principal
from repositories.organization import SqlOrganizationRepository
from api.candidate import router as candidate_router
from api.employer import router as employer_router
from api.job import router as job_router
from api.job_compensation import router as job_compensation_router
from api.job_request import router as job_request_router
from api.application import router as application_router
from api.interview import router as interview_router
from api.trade_test import router as trade_test_router
from api.hiring import router as hiring_router
from api.user_profile import router as user_profile_router
from api.recruitment_pipeline import router as recruitment_pipeline_router

app = FastAPI()

app.include_router(candidate_router)
app.include_router(employer_router)
app.include_router(job_router)
app.include_router(job_compensation_router)
app.include_router(job_request_router)
app.include_router(application_router)
app.include_router(interview_router)
app.include_router(trade_test_router)
app.include_router(hiring_router)
app.include_router(user_profile_router)
app.include_router(recruitment_pipeline_router)

_organization_repository = SqlOrganizationRepository()

@app.get("/api/me")
async def get_current_user(request: Request):
    principal = get_request_principal(request)

    if not principal:
        return {
            "authenticated": False,
            "user": None,
            "roles": [],
        }

    principal_id = principal.get("id") or ""
    principal_name = principal.get("email") or ""

    claims = principal.get("claims", [])

    def claim_values(claim_type):
        return [
            claim.get("val")
            for claim in claims
            if claim.get("typ") == claim_type
        ]

    group_ids = set(claim_values("groups"))
    token_roles = set(claim_values("roles"))

    authorization_groups = {
        "Administrator": "2a75a7c1-e9b8-4c2d-aaed-aeba636a8a66",
        "HR Manager": "9a977cf0-7c9f-4024-9415-357a8a4292bc",
        "Employer Manager": "7088ce1f-8e01-4c7c-88fd-a257721a35df",
        "Candidate": "0869b2d7-2fa1-4c4a-acfd-f5370cf955a6",
    }

    roles = set(token_roles)

    for role, group_id in authorization_groups.items():
        if group_id in group_ids:
            roles.add(role)

    if not roles:
        roles.add("Employee")

    memberships = _organization_repository.get_active_memberships(
        principal_id
    )

    if (
        os.environ.get("TBBD_ENV") == "development"
        and os.environ.get("TBBD_LOCAL_AUTH") == "1"
        and principal_id == "local-administrator-001"
    ):
        class LocalOrganizationMembership:
            user_id = principal_id
            organization_id = "005F50D3-26AB-F111-9B32-000D3AC9134A"
            status = "active"

        memberships = [LocalOrganizationMembership()]

    authorization_context = build_authorization_context(
        user_id=principal_id,
        roles=roles,
        memberships=memberships,
    )

    return {
        "authenticated": True,
        "user": {
            "id": principal_id,
            "email": principal_name,
            "name": next(
                iter(claim_values("name")),
                principal_name,
            ),
        },
        "roles": sorted(authorization_context.roles),
        "organization_ids": sorted(
            authorization_context.organization_ids
        ),
    }



@app.get("/healthz")
def healthz():
    return {"status": "ok"}


BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"

app.mount(
    "/assets",
    StaticFiles(directory=DIST_DIR / "assets"),
    name="assets",
)


@app.get("/")
def home():
    return FileResponse(DIST_DIR / "index.html")


def search_hr_documents(query: str):
    endpoint = os.environ.get("SEARCH_ENDPOINT")
    index_name = os.environ.get("SEARCH_INDEX")
    search_key = os.environ.get("SEARCH_KEY")

    if not endpoint:
        raise RuntimeError("SEARCH_ENDPOINT is not configured")

    if not index_name:
        raise RuntimeError("SEARCH_INDEX is not configured")

    if not search_key:
        raise RuntimeError("SEARCH_KEY is not configured")

    url = (
        f"{endpoint.rstrip('/')}/indexes/"
        f"{index_name}/docs/search"
        "?api-version=2024-07-01"
    )

    payload = {
        "search": query,
        "top": 5,
        "select": "uid,snippet_parent_id,doc_url,snippet"
    }

    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "api-key": search_key,
        },
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for item in data.get("value", []):
        doc_url = item.get("doc_url") or ""
        snippet = item.get("snippet") or ""

        # Extract a readable document name from the SharePoint path.
        document_name = doc_url.rsplit("/", 1)[-1] if doc_url else ""

        results.append(
            {
                "document": document_name,
                "source": doc_url,
                "score": item.get("@search.score"),
                "snippet": snippet,
            }
        )

    return results


@app.post("/mcp")
async def handle_mcp(request: Request):
    try:
        body = await request.json()

        method = body.get("method")
        request_id = body.get("id", 1)

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "Semantic_Hybrid_Search",
                            "description": (
                                "Search TBBD HR policy documents in "
                                "Azure AI Search and return relevant "
                                "policy sources and snippets."
                            ),
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": (
                                            "The employee's HR-related "
                                            "question to search for."
                                        ),
                                    }
                                },
                                "required": ["query"],
                            },
                        }
                    ]
                },
            }

        if method == "tools/call":
            params = body.get("params", {})
            arguments = params.get("arguments", {})
            query = arguments.get("query", "").strip()

            if not query:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": "Query is required",
                }

            results = search_hr_documents(query)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": results
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": f"Unknown method: {method}",
        }

    except requests.HTTPError as e:
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1) if "body" in locals() else 1,
            "error": f"Azure AI Search HTTP error: {str(e)}",
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1) if "body" in locals() else 1,
            "error": str(e),
        }
