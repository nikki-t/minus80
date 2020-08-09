# Standard library imports
from email.mime.text import MIMEText
import smtplib
import unittest
from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch, call

# Local application imports
from app.Email import Email

class TestEmail(unittest.TestCase):
    """ Test methods from Email Class"""

    @mock.patch.dict('app.mail_data.mail_data', {'it_email': 'it@test.edu', \
        'sender': 'sender@test.edu', 'mail_password': 'test123', 
        'imap_server': 'smtp.test.edu', 'port': 465} )
    def test_email_object(self):
        """ Test Email object creation """

        # Create new Email object
        recipient = 'recipient@test.edu'
        subject = 'test of email object creation'
        body = 'this is the body of the test email.'
        email = Email(recipient, subject, body)

        # Assert expected results of str function; state of object upon creation        
        email_string = (
            f"IMAP server: smtp.test.edu"
            f"\nPort: 465"
            f"\nSender: sender@test.edu"
            f"\nRecipient: recipient@test.edu"
            f"\nSubject: test of email object creation"
            f"\nBody: this is the body of the test email."
        )
        self.assertEqual(str(email), email_string)

    @patch("smtplib.SMTP_SSL")
    @mock.patch.dict('app.mail_data.mail_data', {'it_email': 'it@test.edu', \
        'sender': 'sender@test.edu', 
        'mail_password': 'test123', 'imap_server': 'smtp.test.edu', 'port': 465} )
    def test_send_mail(self, mock_smtp_ssl):
        """Tests SMTP object functionality for an Email object"""
        
        # Create Email object
        recipient = 'recipient@test.edu'
        subject = 'test of email object creation'
        body = 'this is the body of the test email.'
        email = Email(recipient, subject, body)

        # Create message body for comparison
        message = MIMEText(body, "plain")
        message["Subject"] = subject
        message["From"] = 'sender@test.edu'
        message["To"] = recipient

        # Send an email
        email.send_email()

        # Object returned from smtp context manager
        mock_smtp_cm = mock_smtp_ssl.return_value.__enter__.return_value

        # Assert login was called once
        mock_smtp_cm.login.assert_called_once_with('sender@test.edu', 'test123')

        # Assert send mail called once
        mock_smtp_cm.sendmail.assert_called_once_with('sender@test.edu', \
            recipient, message.as_string())


if __name__ == "__main__":
    unittest.main()