-- Migration 017: Hiring Workflow
-- Creates persistent Hiring readiness and Job Offer records.
-- Does not modify Interview or Trade Test outcomes.

IF OBJECT_ID('dbo.hiring_records', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.hiring_records (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_hiring_records PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_hiring_records_status
            DEFAULT N'ready_for_hiring',

        readiness_source NVARCHAR(30) NOT NULL,

        waiver_reason NVARCHAR(1000) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_hiring_records_created_at
            DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_hiring_records_updated_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_hiring_records_application
            FOREIGN KEY (application_id)
            REFERENCES dbo.applications(id),

        CONSTRAINT UQ_hiring_records_application
            UNIQUE (application_id),

        CONSTRAINT CK_hiring_records_status
            CHECK (
                status IN (
                    N'ready_for_hiring',
                    N'offered',
                    N'hired'
                )
            ),

        CONSTRAINT CK_hiring_records_readiness_source
            CHECK (
                readiness_source IN (
                    N'interview_pass',
                    N'trade_test_pass',
                    N'waived'
                )
            ),

        CONSTRAINT CK_hiring_records_waiver_reason
            CHECK (
                (
                    readiness_source = N'waived'
                    AND NULLIF(LTRIM(RTRIM(waiver_reason)), N'') IS NOT NULL
                )
                OR
                (
                    readiness_source <> N'waived'
                    AND waiver_reason IS NULL
                )
            )
    );
END
GO

IF OBJECT_ID('dbo.job_offers', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_offers (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_job_offers PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        hiring_record_id UNIQUEIDENTIFIER NOT NULL,

        application_id UNIQUEIDENTIFIER NOT NULL,

        offer_title NVARCHAR(250) NOT NULL,

        employment_type NVARCHAR(50) NULL,

        salary_amount DECIMAL(18, 2) NULL,

        salary_currency NVARCHAR(10) NULL,

        start_date DATE NULL,

        offer_expiry_date DATE NULL,

        terms_and_conditions NVARCHAR(MAX) NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_job_offers_status
            DEFAULT N'Draft',

        offered_at DATETIME2(3) NULL,

        accepted_at DATETIME2(3) NULL,

        rejected_at DATETIME2(3) NULL,

        withdrawn_at DATETIME2(3) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_offers_created_at
            DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_offers_updated_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_job_offers_hiring_record
            FOREIGN KEY (hiring_record_id)
            REFERENCES dbo.hiring_records(id),

        CONSTRAINT FK_job_offers_application
            FOREIGN KEY (application_id)
            REFERENCES dbo.applications(id),

        CONSTRAINT CK_job_offers_status
            CHECK (
                status IN (
                    N'Draft',
                    N'Sent',
                    N'Accepted',
                    N'Rejected',
                    N'Withdrawn'
                )
            ),

        CONSTRAINT CK_job_offers_salary
            CHECK (
                salary_amount IS NULL
                OR salary_amount >= 0
            ),

        CONSTRAINT CK_job_offers_expiry
            CHECK (
                offer_expiry_date IS NULL
                OR offer_expiry_date >= '2000-01-01'
            )
    );
END
GO

CREATE INDEX IX_hiring_records_status
    ON dbo.hiring_records(status);
GO

CREATE INDEX IX_job_offers_application
    ON dbo.job_offers(application_id);
GO

CREATE UNIQUE INDEX UX_job_offers_active_hiring_record
    ON dbo.job_offers(hiring_record_id)
    WHERE status IN (N'Draft', N'Sent', N'Accepted');
GO

CREATE INDEX IX_job_offers_status
    ON dbo.job_offers(status);
GO
