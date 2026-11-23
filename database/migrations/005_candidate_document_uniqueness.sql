/*
    TBBD HR Portal
    Migration 005
    Candidate Profile Document Uniqueness

    Enforces:
      - One profile-level passport per candidate
      - One profile-level resume per candidate

    Application documents remain unrestricted.

    This migration is intentionally idempotent.
*/

SET NOCOUNT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    IF NOT EXISTS (
        SELECT 1
        FROM sys.indexes
        WHERE object_id = OBJECT_ID(N'dbo.documents')
          AND name = N'UQ_documents_candidate_passport'
    )
    BEGIN
        CREATE UNIQUE INDEX UQ_documents_candidate_passport
        ON dbo.documents (candidate_id)
        WHERE application_id IS NULL
          AND document_type = N'passport';
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM sys.indexes
        WHERE object_id = OBJECT_ID(N'dbo.documents')
          AND name = N'UQ_documents_candidate_resume'
    )
    BEGIN
        CREATE UNIQUE INDEX UQ_documents_candidate_resume
        ON dbo.documents (candidate_id)
        WHERE application_id IS NULL
          AND document_type = N'resume';
    END;

    COMMIT TRANSACTION;

    PRINT 'Migration 005 completed successfully.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
