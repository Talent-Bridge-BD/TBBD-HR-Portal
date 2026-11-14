/*
    Add Candidate organization membership
    TBBD HR Portal
*/

INSERT INTO dbo.organization_memberships
(
    organization_id,
    user_id,
    role,
    status
)
VALUES
(
    '005f50d3-26ab-f111-9b32-000d3ac9134a',
    'c18aae4e-1d96-4ba8-a754-4658128aff83',
    'Candidate',
    'active'
);