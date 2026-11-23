-- TBBD Overseas Recruitment
-- Migration 007: Job document management
--
-- This migration adds document metadata for overseas recruitment jobs.
-- Existing candidate/application documents are preserved.
-- LOCAL MIGRATION ONLY - DO NOT EXECUTE AGAINST PRODUCTION YET.

IF OBJECT_ID('dbo.job_documents', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_documents (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_job_documents PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        job_id UNIQUEIDENTIFIER NOT NULL,

        document_type NVARCHAR(50) NOT NULL,
        document_name NVARCHAR(250) NOT NULL,

        blob_container NVARCHAR(250) NULL,
        blob_path NVARCHAR(1000) NULL,

        mime_type NVARCHAR(150) NULL,
        file_size BIGINT NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_job_documents_status DEFAULT 'submitted',

        notes NVARCHAR(MAX) NULL,

        uploaded_by UNIQUEIDENTIFIER NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_documents_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_job_documents_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_job_documents_job
            FOREIGN KEY (job_id) REFERENCES dbo.jobs(id),

        CONSTRAINT CK_job_documents_type
            CHECK (
                document_type IN (
                    'demand_letter',
                    'power_of_attorney',
                    'recruitment_agreement',
                    'employment_contract',
                    'salary_sheet',
                    'visa_document',
                    'medical_requirement',
                    'interview_schedule',
                    'supporting_document'
                )
            ),

        CONSTRAINT CK_job_documents_status
            CHECK (
                status IN (
                    'submitted',
                    'verified',
                    'rejected'
                )
            ),

        CONSTRAINT CK_job_documents_file_size
            CHECK (
                file_size IS NULL
                OR file_size >= 0
            )
    );
END
GO
