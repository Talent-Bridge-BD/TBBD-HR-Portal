/*
    TBBD HR Portal
    Migration 006
    Candidate Profile Photo

    Adds:
      - profile_photo as a supported document type
      - one profile-level profile photo per candidate

    Existing application document types are preserved.

    This migration is intentionally idempotent.
*/

SET NOCOUNT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    IF EXISTS (
        SELECT 1
        FROM sys.check_constraints
        WHERE parent_object_id = OBJECT_ID(N'dbo.documents')
          AND name = N'CK_documents_type'
    )
    BEGIN
        ALTER TABLE dbo.documents
            DROP CONSTRAINT CK_documents_type;
    END;

    ALTER TABLE dbo.documents
        ADD CONSTRAINT CK_documents_type
        CHECK (document_type IN (
            N'resume',
            N'certificate',
            N'passport',
            N'profile_photo',
            N'identity',
            N'identification',
            N'cover_letter',
            N'application_document',
            N'other'
        ));

    IF NOT EXISTS (
        SELECT 1
        FROM sys.indexes
        WHERE object_id = OBJECT_ID(N'dbo.documents')
          AND name = N'UQ_documents_candidate_profile_photo'
    )
    BEGIN
        CREATE UNIQUE INDEX UQ_documents_candidate_profile_photo
        ON dbo.documents (candidate_id)
        WHERE application_id IS NULL
          AND document_type = N'profile_photo';
    END;

    COMMIT TRANSACTION;

    PRINT 'Migration 006 completed successfully.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
