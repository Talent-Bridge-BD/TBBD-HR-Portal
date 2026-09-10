-- Candidate Profile V1 corrections
-- Applied after 005_candidate_profile.sql.

IF COL_LENGTH(N'dbo.candidates', N'current_company') IS NULL
BEGIN
    ALTER TABLE dbo.candidates
        ADD current_company NVARCHAR(200) NULL;
END;
GO

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
GO

ALTER TABLE dbo.documents
    ADD CONSTRAINT CK_documents_type
    CHECK (document_type IN (
        N'resume',
        N'certificate',
        N'passport',
        N'identity',
        N'identification',
        N'cover_letter',
        N'application_document',
        N'other'
    ));
GO

IF EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE parent_object_id = OBJECT_ID(N'dbo.candidate_experience')
      AND name = N'CK_candidate_experience_current'
)
BEGIN
    ALTER TABLE dbo.candidate_experience
        DROP CONSTRAINT CK_candidate_experience_current;
END;
GO

ALTER TABLE dbo.candidate_experience
    ADD CONSTRAINT CK_candidate_experience_current
    CHECK (
        (currently_working = 1 AND end_date IS NULL)
        OR
        (currently_working = 0 AND end_date IS NOT NULL)
    );
GO
