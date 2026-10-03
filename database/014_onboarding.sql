-- Migration 014: Candidate Onboarding
-- Creates application-level onboarding records for candidates
-- progressing through the overseas recruitment lifecycle.

IF OBJECT_ID('dbo.onboarding', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.onboarding (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_onboarding PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        employer_name NVARCHAR(250) NULL,
        job_title NVARCHAR(250) NULL,

        joining_date DATE NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_onboarding_status DEFAULT N'Pending',

        contract_signed BIT NOT NULL
            CONSTRAINT DF_onboarding_contract_signed DEFAULT 0,

        documents_verified BIT NOT NULL
            CONSTRAINT DF_onboarding_documents_verified DEFAULT 0,

        orientation_completed BIT NOT NULL
            CONSTRAINT DF_onboarding_orientation_completed DEFAULT 0,

        accommodation_arranged BIT NOT NULL
            CONSTRAINT DF_onboarding_accommodation_arranged DEFAULT 0,

        transport_arranged BIT NOT NULL
            CONSTRAINT DF_onboarding_transport_arranged DEFAULT 0,

        notes NVARCHAR(MAX) NULL,

        completed_at DATETIME2(3) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_onboarding_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_onboarding_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_onboarding_application
            FOREIGN KEY (application_id)
            REFERENCES dbo.applications(id),

        CONSTRAINT CK_onboarding_status
            CHECK (
                status IN (
                    N'Pending',
                    N'In Progress',
                    N'Completed',
                    N'Cancelled'
                )
            )
    );

    CREATE INDEX IX_onboarding_application
        ON dbo.onboarding(application_id);

    CREATE INDEX IX_onboarding_status
        ON dbo.onboarding(status);
END
GO
