-- Migration 016: Interview outcomes
-- Adds an explicit interview outcome without overloading interview status.

IF COL_LENGTH('dbo.interviews', 'outcome') IS NULL
BEGIN
    ALTER TABLE dbo.interviews
        ADD outcome NVARCHAR(30) NOT NULL
            CONSTRAINT DF_interviews_outcome DEFAULT N'Pending';

    ALTER TABLE dbo.interviews
        ADD CONSTRAINT CK_interviews_outcome
            CHECK (outcome IN (
                N'Pending',
                N'Pass',
                N'Fail'
            ));
END
GO
