-- TBBD Candidate Approval Workflow
-- REVIEW ONLY: DO NOT EXECUTE AGAINST PRODUCTION YET.
--
-- New candidate identities default to pending approval.
-- Existing candidates are backfilled as approved to preserve access.
-- Approval is separate from profile completion and recruitment workflow.
-- This table intentionally has no foreign key to dbo.candidates because
-- candidates may register before creating their profile.

IF OBJECT_ID(N'dbo.candidate_approvals', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.candidate_approvals (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT DF_candidate_approvals_id DEFAULT NEWID(),

        entra_object_id NVARCHAR(100) NOT NULL,

        approval_status NVARCHAR(20) NOT NULL
            CONSTRAINT DF_candidate_approvals_status
            DEFAULT N'pending',

        reviewed_by NVARCHAR(320) NULL,
        reviewed_at DATETIME2(3) NULL,
        approval_notes NVARCHAR(2000) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_approvals_created_at
            DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_approvals_updated_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_candidate_approvals
            PRIMARY KEY (id),

        CONSTRAINT UQ_candidate_approvals_entra_object_id
            UNIQUE (entra_object_id),

        CONSTRAINT CK_candidate_approvals_status
            CHECK (
                approval_status IN (
                    N'pending',
                    N'approved',
                    N'rejected'
                )
            )
    );

    CREATE INDEX IX_candidate_approvals_status_created_at
        ON dbo.candidate_approvals (
            approval_status,
            created_at DESC
        );
END;

-- Preserve access for existing candidate profiles.
-- Insert only identities without an approval record; reruns never
-- reset an existing pending, approved, or rejected decision.
IF OBJECT_ID(N'dbo.candidates', N'U') IS NULL
BEGIN
    THROW 50001,
        'dbo.candidates must exist before applying candidate approval migration.',
        1;
END;

INSERT INTO dbo.candidate_approvals (entra_object_id,
    approval_status)
SELECT
    c.entra_object_id,
    N'approved'

FROM dbo.candidates AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.candidate_approvals AS a
    WHERE a.entra_object_id = c.entra_object_id
);
