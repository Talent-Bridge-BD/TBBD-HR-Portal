-- Migration 011: Candidate Medical Examinations
-- Creates candidate/application-level medical examination records.

IF OBJECT_ID('dbo.medical_examinations', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.medical_examinations (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_medical_examinations PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),

        application_id UNIQUEIDENTIFIER NOT NULL,

        medical_center NVARCHAR(250) NULL,
        examination_date DATETIME2(3) NULL,
        doctor_name NVARCHAR(200) NULL,
        medical_type NVARCHAR(100) NULL,

        status NVARCHAR(30) NOT NULL
            CONSTRAINT DF_medical_examinations_status DEFAULT N'Scheduled',

        result NVARCHAR(30) NOT NULL
            CONSTRAINT DF_medical_examinations_result DEFAULT N'Pending',

        report_notes NVARCHAR(MAX) NULL,
        completed_at DATETIME2(3) NULL,

        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_medical_examinations_created_at DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_medical_examinations_updated_at DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_medical_examinations_application
            FOREIGN KEY (application_id) REFERENCES dbo.applications(id),

        CONSTRAINT CK_medical_examinations_status
            CHECK (status IN (N'Scheduled', N'In Progress', N'Completed', N'Cancelled')),

        CONSTRAINT CK_medical_examinations_result
            CHECK (result IN (N'Pending', N'Fit', N'Unfit', N'Further Review'))
    );
END
GO
