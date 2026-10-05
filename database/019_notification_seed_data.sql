/*
    Notification Management Seed Data

    Adds:
    - Default email configuration
    - Core recruitment notification templates
*/

IF NOT EXISTS (
    SELECT 1
    FROM dbo.notification_email_settings
)
BEGIN

INSERT INTO dbo.notification_email_settings
(
    provider,
    sender_address,
    sender_name,
    is_active
)
VALUES
(
    'Microsoft Graph',
    'notifications@talentbridgebd.com',
    'Talent Bridge BD Workplace Hub',
    1
);

END;


IF NOT EXISTS (
    SELECT 1
    FROM dbo.notification_templates
    WHERE template_code = 'APPLICATION_RECEIVED'
)
BEGIN

INSERT INTO dbo.notification_templates
(
    template_code,
    name,
    event_type,
    subject,
    html_body,
    is_active
)
VALUES
(
    'APPLICATION_RECEIVED',
    'Candidate Application Received',
    'APPLICATION_RECEIVED',
    'Application Received - {{job_title}}',
    '<p>Your application has been received successfully.</p>',
    1
);

END;


IF NOT EXISTS (
    SELECT 1
    FROM dbo.notification_templates
    WHERE template_code = 'INTERVIEW_SCHEDULED'
)
BEGIN

INSERT INTO dbo.notification_templates
(
    template_code,
    name,
    event_type,
    subject,
    html_body,
    is_active
)
VALUES
(
    'INTERVIEW_SCHEDULED',
    'Interview Scheduled',
    'INTERVIEW_SCHEDULED',
    'Interview Scheduled - {{candidate_name}}',
    '<p>Your interview has been scheduled.</p>',
    1
);

END;


IF NOT EXISTS (
    SELECT 1
    FROM dbo.notification_templates
    WHERE template_code = 'OFFER_RELEASED'
)
BEGIN

INSERT INTO dbo.notification_templates
(
    template_code,
    name,
    event_type,
    subject,
    html_body,
    is_active
)
VALUES
(
    'OFFER_RELEASED',
    'Employment Offer Released',
    'OFFER_RELEASED',
    'Employment Offer - {{job_title}}',
    '<p>Your employment offer is available.</p>',
    1
);

END;


IF NOT EXISTS (
    SELECT 1
    FROM dbo.notification_templates
    WHERE template_code = 'ONBOARDING_STARTED'
)
BEGIN

INSERT INTO dbo.notification_templates
(
    template_code,
    name,
    event_type,
    subject,
    html_body,
    is_active
)
VALUES
(
    'ONBOARDING_STARTED',
    'Onboarding Started',
    'ONBOARDING_STARTED',
    'Welcome to Talent Bridge BD',
    '<p>Your onboarding process has started.</p>',
    1
);

END;
