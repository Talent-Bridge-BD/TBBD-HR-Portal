-- TBBD Overseas Recruitment
-- Migration 006: Visa & deployment configuration
--
-- This migration adds visa and deployment information
-- for overseas recruitment jobs.
-- Existing jobs and recruitment relationships are preserved.
-- LOCAL MIGRATION ONLY - DO NOT EXECUTE AGAINST PRODUCTION YET.

IF OBJECT_ID('dbo.job_visa_deployment', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_visa_deployment (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_job_visa_deployment PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        job_id UNIQUEIDENTIFIER NOT NULL,

        visa_type NVARCHAR(100) NULL,
        visa_quantity INT NULL,
        visa_expiry_date DATE NULL,
        visa_status NVARCHAR(50) NULL,

        deployment_deadline DATE NULL,
        expected_departure_date DATE NULL,
        arrival_date DATE NULL,
        employer_joining_date DATE NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_visa_deployment_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_visa_deployment_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_job_visa_deployment_job
            FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),

        CONSTRAINT UQ_job_visa_deployment_job
            UNIQUE (job_id),

        CONSTRAINT CK_job_visa_deployment_visa_quantity
            CHECK (
                visa_quantity IS NULL
                OR visa_quantity >= 0
            )
    );
END
GO
