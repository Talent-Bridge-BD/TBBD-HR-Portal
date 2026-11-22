from fastapi import APIRouter, HTTPException, Request

from api.administrator_organizations import require_admin
from repositories.application_roles import application_role_repository
from repositories.audit_logs import AuditLogRepository
from services.local_auth import get_request_principal


router = APIRouter(
    prefix="/api/administrator/candidate-roles",
    tags=["administrator-candidate-roles"],
)

_repository = application_role_repository
_audit_log_repository = AuditLogRepository()


def _write_audit(
    *,
    principal,
    target_user_id,
    action,
    status,
    previous_status,
    new_status,
    outcome,
):
    _audit_log_repository.create_log(
        user_id=str(principal.get("id") or ""),
        user_email=principal.get("email"),
        user_name=principal.get("name"),
        organization_id=None,
        event_type="candidate_role_assignment",
        action=action,
        entity_type="application_role_assignment",
        entity_id=target_user_id,
        status=status,
        details={
            "target_user_id": target_user_id,
            "role": "Candidate",
            "previous_status": previous_status,
            "new_status": new_status,
            "outcome": outcome,
        },
    )


def _try_failure_audit(
    principal, target_user_id, action, previous_status, new_status, outcome
):
    try:
        _write_audit(
            principal=principal,
            target_user_id=target_user_id,
            action=action,
            status="failure",
            previous_status=previous_status,
            new_status=new_status,
            outcome=outcome,
        )
    except Exception:
        # Do not hide the original operation failure if audit storage is down.
        pass


def _change_candidate_role(request: Request, user_id: str, action: str):
    require_admin(request)

    principal = get_request_principal(request) or {}
    actor_id = str(principal.get("id") or "").strip()
    target_user_id = user_id.strip() if isinstance(user_id, str) else ""

    if not actor_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated administrator required",
        )

    if not target_user_id or len(target_user_id) > 200:
        raise HTTPException(
            status_code=422,
            detail="Provide a valid target user ID",
        )

    previous_status = None
    new_status = None
    changed = False

    try:
        previous_status = _repository.assignment_status(
            target_user_id, "Candidate"
        )

        if action == "grant":
            if previous_status != "active":
                _repository.grant_role(
                    target_user_id, "Candidate", assigned_by=actor_id
                )
                new_status = "active"
                changed = True
            else:
                new_status = "active"

        elif action == "revoke":
            if previous_status not in (None, "revoked"):
                _repository.revoke_role(
                    target_user_id, "Candidate", assigned_by=actor_id
                )
                new_status = "revoked"
                changed = True
            else:
                new_status = previous_status

        else:
            raise HTTPException(status_code=422, detail="Invalid role action")

    except HTTPException:
        raise
    except Exception as exc:
        _try_failure_audit(
            principal,
            target_user_id,
            action,
            previous_status,
            new_status,
            "role_operation_failed",
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to change the Candidate role assignment",
        ) from exc

    outcome = "changed" if changed else "unchanged"

    try:
        _write_audit(
            principal=principal,
            target_user_id=target_user_id,
            action=action,
            status="success",
            previous_status=previous_status,
            new_status=new_status,
            outcome=outcome,
        )
    except Exception as exc:
        detail = (
            "The role change was applied, but audit logging failed. "
            "Verify the current role assignment before retrying."
            if changed
            else "The role assignment was unchanged, but audit logging failed."
        )
        raise HTTPException(status_code=500, detail=detail) from exc

    return {
        "user_id": target_user_id,
        "role": "Candidate",
        "action": action,
        "previous_status": previous_status,
        "assignment_status": new_status,
        "status": "updated" if changed else "unchanged",
    }


@router.post("/{user_id}/grant")
def grant_candidate_role(user_id: str, request: Request):
    return _change_candidate_role(request, user_id, "grant")


@router.post("/{user_id}/revoke")
def revoke_candidate_role(user_id: str, request: Request):
    return _change_candidate_role(request, user_id, "revoke")
