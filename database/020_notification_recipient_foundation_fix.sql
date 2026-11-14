/*
    TBBD HR Portal
    Notification Recipient Foundation Fix

    Purpose:
      Allow employer/HR notifications that are not tied
      to a specific candidate.

    Existing candidate notifications remain unchanged:
      candidate_id continues to be populated for them.

    Safe:
      - Does not create a second notifications table.
      - Existing notification rows are preserved.
      - Safe to execute more than once.
*/

SET XACT_ABORT ON;

BEGIN TRANSACTION;

------------------------------------------------------------
-- 1. Allow notifications without a candidate
------------------------------------------------------------

IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.notifications')
      AND name = 'candidate_id'
      AND is_nullable = 0
)
BEGIN
    ALTER TABLE dbo.notifications
        ALTER COLUMN candidate_id UNIQUEIDENTIFIER NULL;
END;

COMMIT TRANSACTION;
