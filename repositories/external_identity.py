from __future__ import annotations

from collections.abc import Callable
from typing import Any


class SqlExternalIdentityMappingRepository:
    """Read and create administrator-verified external identity mappings.

    The supplied connection factory must return the same Azure SQL connection
    type used by SqlOrganizationRepository. No schema is created here.
    """

    def __init__(self, connection_factory: Callable[[], Any]):
        self._connection = connection_factory

    def get_mapping(
        self,
        *,
        provider: str,
        tenant_id: str,
        external_object_id: str,
    ) -> dict | None:
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    CONVERT(nvarchar(36), id) AS id,
                    provider,
                    tenant_id,
                    external_object_id,
                    application_user_id,
                    status,
                    CONVERT(nvarchar(33), verified_at, 126) AS verified_at,
                    verified_by,
                    verification_method
                FROM dbo.external_identity_mappings
                WHERE provider = ?
                  AND tenant_id = ?
                  AND external_object_id = ?
                """,
                provider,
                tenant_id,
                external_object_id,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return {
                "id": str(row.id),
                "provider": str(row.provider),
                "tenant_id": str(row.tenant_id),
                "external_object_id": str(row.external_object_id),
                "application_user_id": str(row.application_user_id),
                "status": str(row.status),
                "verified_at": row.verified_at,
                "verified_by": str(row.verified_by) if row.verified_by else None,
                "verification_method": (
                    str(row.verification_method) if row.verification_method else None
                ),
            }

    def create_active_mapping(
        self,
        *,
        provider: str,
        tenant_id: str,
        external_object_id: str,
        application_user_id: str,
        verified_by: str,
        verification_method: str = "administrator_attestation",
    ) -> dict:
        import uuid

        mapping_id = str(uuid.uuid4())
        with self._connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO dbo.external_identity_mappings (
                    id, provider, tenant_id, external_object_id,
                    application_user_id, status, verified_at, verified_by,
                    verification_method, created_at, updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, N'Active', SYSUTCDATETIME(), ?, ?,
                    SYSUTCDATETIME(), SYSUTCDATETIME()
                )
                """,
                mapping_id,
                provider,
                tenant_id,
                external_object_id,
                application_user_id,
                verified_by,
                verification_method,
            )
            connection.commit()

        return {
            "id": mapping_id,
            "provider": provider,
            "tenant_id": tenant_id,
            "external_object_id": external_object_id,
            "application_user_id": application_user_id,
            "status": "Active",
            "verified_by": verified_by,
            "verification_method": verification_method,
        }
