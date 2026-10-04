from services.email_service import EmailService


email_service = EmailService()


def send_candidate_application_received(
    candidate_email,
    candidate_name,
    job_title
):

    html = f"""
    <h2>Hello {candidate_name}</h2>

    <p>
    Your application for
    <strong>{job_title}</strong>
    has been received.
    </p>

    <p>
    Talent Bridge BD Recruitment Team
    </p>
    """

    return email_service.send_email(
        recipient=candidate_email,
        subject="Application Received - Talent Bridge BD",
        html_content=html
    )