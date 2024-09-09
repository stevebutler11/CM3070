import os
import smtplib
from src.db.models import EmailRecipient
from src.db.database import db_session


class Notification:
    """Class to send notifications to system users."""

    @staticmethod
    def send_emails(
        user: str, pwd: str, emails: list[str], subject: str, body: str
    ) -> None:
        """Send emails to users via gmail server with credentials from environment."""

        # modified from below
        # https://stackoverflow.com/questions/10147455/how-to-send-an-email-with-gmail-as-provider-using-python
        msg = f"From: {user}\nTo: {', '.join(emails)}\nSubject: {subject}\n\n{body}"

        try:
            server = smtplib.SMTP("smtp.googlemail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(user, pwd)
            server.sendmail(user, emails, msg)
            server.close()
            print("successfully sent the mail")
        except Exception as e:
            print(user)
            print(pwd)
            print("failed to send mail", e)
