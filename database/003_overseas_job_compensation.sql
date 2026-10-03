-- TBBD Overseas Recruitment
-- Migration 003: Job compensation & benefits
--
-- This migration adds compensation and benefit configuration
-- for overseas recruitment jobs.
-- Existing jobs and recruitment relationships are preserved.
-- LOCAL MIGRATION ONLY - DO NOT EXECUTE AGAINST PRODUCTION YET.

IF OBJECT_ID('dbo.job_compensation', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_compensation (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_job_compensation PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        job_id UNIQUEIDENTIFIER NOT NULL,

        salary_currency NVARCHAR(10) NULL,
        basic_salary DECIMAL(18, 2) NULL,
        overtime_rate DECIMAL(18, 2) NULL,

        food_provided BIT NOT NULL
            CONSTRAINT DF_job_compensation_food_provided DEFAULT 0,

        accommodation_provided BIT NOT NULL
            CONSTRAINT DF_job_compensation_accommodation_provided DEFAULT 0,

        transportation_provided BIT NOT NULL
            CONSTRAINT DF_job_compensation_transportation_provided DEFAULT 0,

        medical_coverage BIT NOT NULL
            CONSTRAINT DF_job_compensation_medical_coverage DEFAULT 0,

        air_ticket_provided BIT NOT NULL
            CONSTRAINT DF_job_compensation_air_ticket_provided DEFAULT 0,

        leave_entitlement NVARCHAR(100) NULL,
        other_benefits NVARCHAR(MAX) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_compensation_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_compensation_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_job_compensation_job
            FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),

        CONSTRAINT UQ_job_compensation_job
            UNIQUE (job_id),

        CONSTRAINT CK_job_compensation_basic_salary
            CHECK (basic_salary IS NULL OR basic_salary >= 0),

        CONSTRAINT CK_job_compensation_overtime_rate
            CHECK (overtime_rate IS NULL OR overtime_rate >= 0)
    );
END
GO
