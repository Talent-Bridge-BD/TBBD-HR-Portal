-- TBBD Overseas Recruitment
-- Migration 005: Recruitment workflow configuration
--
-- This migration defines the recruitment stages required
-- for each overseas recruitment job.
-- Existing jobs and recruitment relationships are preserved.
-- LOCAL MIGRATION ONLY - DO NOT EXECUTE AGAINST PRODUCTION YET.

IF OBJECT_ID('dbo.job_workflow', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_workflow (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_job_workflow PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        job_id UNIQUEIDENTIFIER NOT NULL,

        screening_required BIT NOT NULL
            CONSTRAINT DF_job_workflow_screening_required DEFAULT 1,

        interview_required BIT NOT NULL
            CONSTRAINT DF_job_workflow_interview_required DEFAULT 1,

        trade_test_required BIT NOT NULL
            CONSTRAINT DF_job_workflow_trade_test_required DEFAULT 0,

        medical_required BIT NOT NULL
            CONSTRAINT DF_job_workflow_medical_required DEFAULT 1,

        visa_required BIT NOT NULL
            CONSTRAINT DF_job_workflow_visa_required DEFAULT 1,

        ticketing_required BIT NOT NULL
            CONSTRAINT DF_job_workflow_ticketing_required DEFAULT 1,

        deployment_required BIT NOT NULL
            CONSTRAINT DF_job_workflow_deployment_required DEFAULT 1,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_workflow_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_workflow_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_job_workflow_job
            FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),

        CONSTRAINT UQ_job_workflow_job
            UNIQUE (job_id)
    );
END
GO
