from services.email_service import EmailService

email = EmailService()

result = email.send_email(
    recipient="mdnaieem0141@gmail.com",
    subject="TBBD HR Portal - Azure Email Test",
    html_content="""
    <html>
      <body>
        <h2>TBBD HR Portal Email Test</h2>
        <p>Hello MD NAIEEM,</p>
        <p>
          This is a test email from Talent Bridge BD HR Portal.
        </p>
        <p>
          Azure Communication Services Email integration is working successfully.
        </p>
        <br>
        <p>Regards,<br>
        Talent Bridge BD HR Portal</p>
      </body>
    </html>
    """,
    plain_text="""
Hello MD NAIEEM,

This is a test email from Talent Bridge BD HR Portal.

Azure Communication Services Email integration is working successfully.

Regards,
Talent Bridge BD HR Portal
"""
)

print(result)