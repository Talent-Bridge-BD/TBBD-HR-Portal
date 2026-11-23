/*
  TBBD HR Portal - Employer access request organization relationship.

  REVIEW ONLY - DO NOT EXECUTE AGAINST PRODUCTION.

  Adds a nullable organization reference to employer access requests.
  Approval code must create the organization and update the request
  within one SQL transaction.

  The filtered unique index permits multiple NULL values while ensuring
  that each provisioned organization is linked to at most one request.
*/

IF OBJECT_ID(N'dbo.employer_access_requests', N'U') IS NOT NULL
   AND COL_LENGTH(
       N'dbo.employer_access_requests',
       N'organization_id'
   ) IS NULL
BEGIN
    ALTER TABLE dbo.employer_access_requests
        ADD organization_id UNIQUEIDENTIFIER NULL;
END;
GO

IF OBJECT_ID(N'dbo.employer_access_requests', N'U') IS NOT NULL
   AND COL_LENGTH(
       N'dbo.employer_access_requests',
       N'organization_id'
   ) IS NOT NULL
   AND OBJECT_ID(N'dbo.organizations', N'U') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.foreign_keys
       WHERE name = N'FK_employer_access_requests_organization'
         AND parent_object_id =
             OBJECT_ID(N'dbo.employer_access_requests')
   )
BEGIN
    ALTER TABLE dbo.employer_access_requests
        WITH CHECK ADD CONSTRAINT
        FK_employer_access_requests_organization
        FOREIGN KEY (organization_id)
        REFERENCES dbo.organizations(id);
END;
GO

IF OBJECT_ID(N'dbo.employer_access_requests', N'U') IS NOT NULL
   AND COL_LENGTH(
       N'dbo.employer_access_requests',
       N'organization_id'
   ) IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.indexes
       WHERE object_id =
             OBJECT_ID(N'dbo.employer_access_requests')
         AND name =
             N'UX_employer_access_requests_organization_id'
   )
BEGIN
    CREATE UNIQUE INDEX
        UX_employer_access_requests_organization_id
    ON dbo.employer_access_requests(organization_id)
    WHERE organization_id IS NOT NULL;
END;
GO
