import os
from azure.communication.email import EmailClient


class EmailService:

    def __init__(self):
        connection_string = os.getenv(
            "AZURE_COMMUNICATION_CONNECTION_STRING"
        )

        if not connection_string:
            raise ValueError(
                "AZURE_COMMUNICATION_CONNECTION_STRING missing"
            )

        self.client = EmailClient.from_connection_string(
            connection_string
        )

        self.sender = os.getenv(
            "AZURE_EMAIL_SENDER",
            "notifications@talentbridgebd.com"
        )


    def send_email(
        self,
        recipient,
        subject,
        html_content,
        plain_text=None
    ):

        message = {
            "senderAddress": self.sender,

            "recipients": {
                "to": [
                    {
                        "address": recipient
                    }
                ]
            },

            "content": {
                "subject": subject,
                "html": html_content,
                "plainText": plain_text or ""
            }
        }


        poller = self.client.begin_send(message)

        return poller.result()