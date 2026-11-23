-- TBBD Overseas Recruitment
-- Migration 008: Job approval & governance
--
-- This migration adds approval and governance information
-- for overseas recruitment jobs.
-- Existing jobs and recruitment relationships are preserved.
-- LOCAL MIGRATION ONLY - DO NOT EXECUTE AGAINST PRODUCTION YET.

IF OBJECT_ID('dbo.job_approval', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_approval (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_job_approval PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        job_id UNIQUEIDENTIFIER NOT NULL,

        approval_status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_job_approval_status DEFAULT 'pending',

        approved_by UNIQUEIDENTIFIER NULL,
        approved_at DATETIME2(3) NULL,
        approval_notes NVARCHAR(MAX) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_approval_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_approval_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_job_approval_job
            FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),

        CONSTRAINT UQ_job_approval_job
            UNIQUE (job_id),

        CONSTRAINT CK_job_approval_status
            CHECK (
                approval_status IN (
                    'pending',
                    'approved',
                    'rejected'
                )
            )
    );
END
GO
