from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

import pyodbc
from azure.identity import DefaultAzureCredential

from models.candidate_certification import CandidateCertification


SERVER = "tbbd-sql-sea.database.windows.net"
DATABASE = "tbbd-hr-db"
DRIVER = "{ODBC Driver 18 for SQL Server}"


class CandidateCertificationRepository(ABC):
    @abstractmethod
    def list_certifications(self, candidate_id: str) -> List[CandidateCertification]:
        raise NotImplementedError

    @abstractmethod
    def get_certification(
        self,
        candidate_id: str,
        certification_id: str,
    ) -> Optional[CandidateCertification]:
        raise NotImplementedError

    @abstractmethod
    def create_certification(
        self,
        candidate_id: str,
        certification_name: str,
        issuing_organization: str,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        credential_id: Optional[str],
    ) -> Optional[CandidateCertification]:
        raise NotImplementedError

    @abstractmethod
    def update_certification(
        self,
        candidate_id: str,
        certification_id: str,
        certification_name: str,
        issuing_organization: str,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        credential_id: Optional[str],
    ) -> Optional[CandidateCertification]:
        raise NotImplementedError

    @abstractmethod
    def delete_certification(
        self,
        candidate_id: str,
        certification_id: str,
    ) -> bool:
        raise NotImplementedError


class SqlCandidateCertificationRepository(CandidateCertificationRepository):
    def __init__(self):
        self.credential = DefaultAzureCredential()

    def _connect(self):
        token = self.credential.get_token(
            "https://database.windows.net/.default"
        )
        token_bytes = token.token.encode("utf-16-le")
        token_struct = bytes(
            len(token_bytes).to_bytes(4, "little")
        ) + token_bytes

        return pyodbc.connect(
            f"DRIVER={DRIVER};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;",
            attrs_before={1256: token_struct},
        )

    def _map_row(self, row) -> CandidateCertification:
        return CandidateCertification(
            id=str(row.id),
            candidate_id=str(row.candidate_id),
            certification_name=row.certification_name,
            issuing_organization=row.issuing_organization,
            issue_date=row.issue_date,
            expiry_date=row.expiry_date,
            credential_id=row.credential_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_certifications(self, candidate_id: str) -> List[CandidateCertification]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    cc.id,
                    cc.candidate_id,
                    cc.certification_name,
                    cc.issuing_organization,
                    cc.issue_date,
                    cc.expiry_date,
                    cc.credential_id,
                    cc.created_at,
                    cc.updated_at
                FROM dbo.candidate_certifications AS cc
                INNER JOIN dbo.candidates AS c
                    ON c.id = cc.candidate_id
                WHERE c.entra_object_id = ?
                ORDER BY
                    cc.issue_date DESC,
                    cc.created_at DESC;
                """,
                candidate_id,
            )
            return [self._map_row(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_certification(
        self,
        candidate_id: str,
        certification_id: str,
    ) -> Optional[CandidateCertification]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    cc.id,
                    cc.candidate_id,
                    cc.certification_name,
                    cc.issuing_organization,
                    cc.issue_date,
                    cc.expiry_date,
                    cc.credential_id,
                    cc.created_at,
                    cc.updated_at
                FROM dbo.candidate_certifications AS cc
                INNER JOIN dbo.candidates AS c
                    ON c.id = cc.candidate_id
                WHERE c.entra_object_id = ?
                  AND cc.id = ?;
                """,
                candidate_id,
                certification_id,
            )
            row = cursor.fetchone()
            return self._map_row(row) if row else None
        finally:
            conn.close()

    def create_certification(
        self,
        candidate_id: str,
        certification_name: str,
        issuing_organization: str,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        credential_id: Optional[str],
    ) -> Optional[CandidateCertification]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO dbo.candidate_certifications (
                    candidate_id,
                    certification_name,
                    issuing_organization,
                    issue_date,
                    expiry_date,
                    credential_id
                )
                OUTPUT
                    INSERTED.id,
                    INSERTED.candidate_id,
                    INSERTED.certification_name,
                    INSERTED.issuing_organization,
                    INSERTED.issue_date,
                    INSERTED.expiry_date,
                    INSERTED.credential_id,
                    INSERTED.created_at,
                    INSERTED.updated_at
                SELECT
                    c.id,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                FROM dbo.candidates AS c
                WHERE c.entra_object_id = ?;
                """,
                certification_name,
                issuing_organization,
                issue_date,
                expiry_date,
                credential_id,
                candidate_id,
            )
            row = cursor.fetchone()
            conn.commit()
            return self._map_row(row) if row else None
        finally:
            conn.close()

    def update_certification(
        self,
        candidate_id: str,
        certification_id: str,
        certification_name: str,
        issuing_organization: str,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        credential_id: Optional[str],
    ) -> Optional[CandidateCertification]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE cc
                SET
                    certification_name = ?,
                    issuing_organization = ?,
                    issue_date = ?,
                    expiry_date = ?,
                    credential_id = ?,
                    updated_at = SYSUTCDATETIME()
                OUTPUT
                    INSERTED.id,
                    INSERTED.candidate_id,
                    INSERTED.certification_name,
                    INSERTED.issuing_organization,
                    INSERTED.issue_date,
                    INSERTED.expiry_date,
                    INSERTED.credential_id,
                    INSERTED.created_at,
                    INSERTED.updated_at
                FROM dbo.candidate_certifications AS cc
                INNER JOIN dbo.candidates AS c
                    ON c.id = cc.candidate_id
                WHERE c.entra_object_id = ?
                  AND cc.id = ?;
                """,
                certification_name,
                issuing_organization,
                issue_date,
                expiry_date,
                credential_id,
                candidate_id,
                certification_id,
            )
            row = cursor.fetchone()
            conn.commit()
            return self._map_row(row) if row else None
        finally:
            conn.close()

    def delete_certification(
        self,
        candidate_id: str,
        certification_id: str,
    ) -> bool:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE cc
                FROM dbo.candidate_certifications AS cc
                INNER JOIN dbo.candidates AS c
                    ON c.id = cc.candidate_id
                WHERE c.entra_object_id = ?
                  AND cc.id = ?;
                """,
                candidate_id,
                certification_id,
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()
