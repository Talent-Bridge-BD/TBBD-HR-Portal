-- TBBD HR Portal: candidate education records
-- Review before executing against Azure SQL.
-- Matches models/candidate_education.py and repositories/candidate_education.py.
-- Creates the table and index only when they do not already exist.

IF OBJECT_ID(N'dbo.candidate_education', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.candidate_education (
        id UNIQUEIDENTIFIER NOT NULL
            CONSTRAINT PK_candidate_education PRIMARY KEY
            DEFAULT NEWSEQUENTIALID(),
        candidate_id UNIQUEIDENTIFIER NOT NULL,
        degree_qualification NVARCHAR(200) NOT NULL,
        institution NVARCHAR(250) NOT NULL,
        field_of_study NVARCHAR(200) NULL,
        start_date DATE NULL,
        end_date DATE NULL,
        description NVARCHAR(MAX) NULL,
        created_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_education_created_at DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(3) NOT NULL
            CONSTRAINT DF_candidate_education_updated_at DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_candidate_education_candidate
            FOREIGN KEY (candidate_id) REFERENCES dbo.candidates(id),
        CONSTRAINT CK_candidate_education_dates
            CHECK (
                start_date IS NULL
                OR end_date IS NULL
                OR end_date >= start_date
            )
    );
END;
GO

IF OBJECT_ID(N'dbo.candidate_education', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE object_id = OBJECT_ID(N'dbo.candidate_education')
         AND name = N'IX_candidate_education_candidate'
   )
BEGIN
    CREATE INDEX IX_candidate_education_candidate
        ON dbo.candidate_education(candidate_id, start_date DESC);
END;
GO
