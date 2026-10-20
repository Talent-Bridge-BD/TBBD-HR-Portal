/*
    TBBD HR Portal
    Migration 007
    Candidate Personal Profile Fields

    Adds missing candidate personal and passport fields.
    Idempotent: safe to run more than once.
    Does not delete or overwrite existing candidate data.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    IF COL_LENGTH('dbo.candidates', 'gender') IS NULL
        ALTER TABLE dbo.candidates ADD gender nvarchar(30) NULL;

    IF COL_LENGTH('dbo.candidates', 'nationality') IS NULL
        ALTER TABLE dbo.candidates ADD nationality nvarchar(100) NULL;

    IF COL_LENGTH('dbo.candidates', 'nid_number') IS NULL
        ALTER TABLE dbo.candidates ADD nid_number nvarchar(100) NULL;

    IF COL_LENGTH('dbo.candidates', 'passport_issue_date') IS NULL
        ALTER TABLE dbo.candidates ADD passport_issue_date date NULL;

    COMMIT TRANSACTION;

    PRINT 'Migration 007 completed successfully.';
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
