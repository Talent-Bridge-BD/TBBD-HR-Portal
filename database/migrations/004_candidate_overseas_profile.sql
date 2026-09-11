/*
    TBBD HR Portal
    Migration 004
    Candidate Overseas Recruitment Profile

    Adds:
      - Career level
      - Passport information
      - International travel readiness
      - Candidate languages

    This migration is intentionally idempotent.
    It does not delete or alter existing candidate data.
*/

SET NOCOUNT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    /* =========================================================
       1. Extend dbo.candidates
       ========================================================= */

    IF COL_LENGTH('dbo.candidates', 'career_level') IS NULL
    BEGIN
        ALTER TABLE dbo.candidates
        ADD career_level nvarchar(50) NULL;
    END;

    IF COL_LENGTH('dbo.candidates', 'passport_number') IS NULL
    BEGIN
        ALTER TABLE dbo.candidates
        ADD passport_number nvarchar(100) NULL;
    END;

    IF COL_LENGTH('dbo.candidates', 'passport_country') IS NULL
    BEGIN
        ALTER TABLE dbo.candidates
        ADD passport_country nvarchar(100) NULL;
    END;

    IF COL_LENGTH('dbo.candidates', 'passport_expiry_date') IS NULL
    BEGIN
        ALTER TABLE dbo.candidates
        ADD passport_expiry_date date NULL;
    END;

    IF COL_LENGTH('dbo.candidates', 'passport_status') IS NULL
    BEGIN
        ALTER TABLE dbo.candidates
        ADD passport_status nvarchar(30) NULL;
    END;

    IF COL_LENGTH('dbo.candidates', 'international_travel_readiness') IS NULL
    BEGIN
        ALTER TABLE dbo.candidates
        ADD international_travel_readiness nvarchar(50) NULL;
    END;

    /* =========================================================
       2. Candidate languages
       ========================================================= */

    IF OBJECT_ID('dbo.candidate_languages', 'U') IS NULL
    BEGIN
        CREATE TABLE dbo.candidate_languages
        (
            id uniqueidentifier NOT NULL
                CONSTRAINT PK_candidate_languages
                PRIMARY KEY
                DEFAULT NEWID(),

            candidate_id uniqueidentifier NOT NULL,

            language_name nvarchar(100) NOT NULL,

            speaking_proficiency nvarchar(30) NULL,

            reading_proficiency nvarchar(30) NULL,

            writing_proficiency nvarchar(30) NULL,

            created_at datetime2 NOT NULL
                CONSTRAINT DF_candidate_languages_created_at
                DEFAULT SYSUTCDATETIME(),

            updated_at datetime2 NOT NULL
                CONSTRAINT DF_candidate_languages_updated_at
                DEFAULT SYSUTCDATETIME(),

            CONSTRAINT FK_candidate_languages_candidate
                FOREIGN KEY (candidate_id)
                REFERENCES dbo.candidates(id)
        );
    END;

    COMMIT TRANSACTION;

    PRINT 'Migration 004 completed successfully.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
