-- Migration 012: Candidate Visa Processing
-- Creates candidate/application-level visa processing records.

IF OBJECT_ID('dbo.visa_processing', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.visa_processing (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_visa_processing PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        visa_type NVARCHAR(100) NULL,
        visa_number NVARCHAR(150) NULL,
        application_number NVARCHAR(150) NULL,

        submission_date DATE NULL,
        approval_date DATE NULL,
        expiry_date DATE NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_visa_processing_status DEFAULT N'Pending',

        sponsor_name NVARCHAR(250) NULL,
        sponsor_reference NVARCHAR(150) NULL,

        notes NVARCHAR(MAX) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_visa_processing_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_visa_processing_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_visa_processing_application
            FOREIGN KEY (application_id) REFERENCES dbo.applications(id),

        CONSTRAINT CK_visa_processing_status
            CHECK (
                status IN (
                    N'Pending',
                    N'Submitted',
                    N'Processing',
                    N'Approved',
                    N'Rejected',
                    N'Expired'
                )
            )
    );
END
GO
