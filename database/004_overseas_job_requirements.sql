-- TBBD Overseas Recruitment
-- Migration 004: Candidate eligibility requirements
--
-- This migration adds candidate eligibility requirements
-- for overseas recruitment jobs.
-- Existing jobs and recruitment relationships are preserved.
-- LOCAL MIGRATION ONLY - DO NOT EXECUTE AGAINST PRODUCTION YET.

IF OBJECT_ID('dbo.job_requirements', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_requirements (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_job_requirements PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        job_id UNIQUEIDENTIFIER NOT NULL,

        minimum_education NVARCHAR(250) NULL,
        minimum_experience DECIMAL(6, 2) NULL,
        maximum_experience DECIMAL(6, 2) NULL,

        required_skills NVARCHAR(MAX) NULL,
        preferred_skills NVARCHAR(MAX) NULL,
        required_certifications NVARCHAR(MAX) NULL,
        language_requirements NVARCHAR(MAX) NULL,

        passport_required BIT NOT NULL
            CONSTRAINT DF_job_requirements_passport_required DEFAULT 0,

        medical_fitness_required BIT NOT NULL
            CONSTRAINT DF_job_requirements_medical_fitness_required DEFAULT 0,

        driving_license_required BIT NOT NULL
            CONSTRAINT DF_job_requirements_driving_license_required DEFAULT 0,

        trade_test_required BIT NOT NULL
            CONSTRAINT DF_job_requirements_trade_test_required DEFAULT 0,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_requirements_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_requirements_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_job_requirements_job
            FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),

        CONSTRAINT UQ_job_requirements_job
            UNIQUE (job_id),

        CONSTRAINT CK_job_requirements_minimum_experience
            CHECK (
                minimum_experience IS NULL
                OR minimum_experience >= 0
            ),

        CONSTRAINT CK_job_requirements_maximum_experience
            CHECK (
                maximum_experience IS NULL
                OR maximum_experience >= 0
            ),

        CONSTRAINT CK_job_requirements_experience_range
            CHECK (
                maximum_experience IS NULL
                OR minimum_experience IS NULL
                OR maximum_experience >= minimum_experience
            )
    );
END
GO
