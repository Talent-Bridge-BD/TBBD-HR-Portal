-- Migration 015: Candidate Screening Assessments
-- Creates application-level screening assessment records.

IF OBJECT_ID('dbo.screening_assessments', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.screening_assessments (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_screening_assessments PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        basic_eligibility NVARCHAR(30) NULL,
        relevant_experience NVARCHAR(30) NULL,
        education NVARCHAR(30) NULL,
        communication NVARCHAR(30) NULL,
        availability NVARCHAR(30) NULL,

        screening_notes NVARCHAR(MAX) NULL,

        recommendation NVARCHAR(30) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_screening_assessments_created_at
            DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_screening_assessments_updated_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_screening_assessments_application
            FOREIGN KEY (application_id)
            REFERENCES dbo.applications(id),

        CONSTRAINT UQ_screening_assessments_application
            UNIQUE (application_id),

        CONSTRAINT CK_screening_assessments_basic_eligibility
            CHECK (
                basic_eligibility IS NULL
                OR basic_eligibility IN (
                    N'Yes',
                    N'No',
                    N'Needs Review'
                )
            ),

        CONSTRAINT CK_screening_assessments_relevant_experience
            CHECK (
                relevant_experience IS NULL
                OR relevant_experience IN (
                    N'Strong',
                    N'Moderate',
                    N'Limited'
                )
            ),

        CONSTRAINT CK_screening_assessments_education
            CHECK (
                education IS NULL
                OR education IN (
                    N'Yes',
                    N'No',
                    N'Needs Review'
                )
            ),

        CONSTRAINT CK_screening_assessments_communication
            CHECK (
                communication IS NULL
                OR communication IN (
                    N'Strong',
                    N'Satisfactory',
                    N'Needs Improvement'
                )
            ),

        CONSTRAINT CK_screening_assessments_availability
            CHECK (
                availability IS NULL
                OR availability IN (
                    N'Immediate',
                    N'1 Month',
                    N'Later'
                )
            ),

        CONSTRAINT CK_screening_assessments_recommendation
            CHECK (
                recommendation IS NULL
                OR recommendation IN (
                    N'Shortlist Candidate',
                    N'Continue Screening',
                    N'Reject Application'
                )
            )
    );
END
GO
