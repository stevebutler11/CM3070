import pytest
from unittest.mock import patch, MagicMock
import smtplib
from src.notification.notification import Notification


@pytest.fixture
def mock_smtp():
    """Mock the SMTP server."""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        yield mock_smtp, mock_server


def test_send_emails_success(mock_smtp):
    """Test that emails are sent successfully."""
    mock_smtp_class, mock_smtp_instance = mock_smtp

    # Test data
    user = "test_user@gmail.com"
    pwd = "test_password"
    emails = ["user1@example.com", "user2@example.com"]
    subject = "Test Subject"
    body = "Test Body"

    # Call the method
    Notification.send_emails(user, pwd, emails, subject, body)

    # Make assertions on calls made
    mock_smtp_class.assert_called_with("smtp.googlemail.com", 587)
    mock_smtp_instance.ehlo.assert_called_once()
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with(user, pwd)
    mock_smtp_instance.sendmail.assert_called_once_with(
        user,
        emails,
        f"From: {user}\nTo: stevebutler11@gmail.com, user2@example.com\nSubject: {subject}\n\n{body}"
    )
    mock_smtp_instance.close.assert_called_once()
