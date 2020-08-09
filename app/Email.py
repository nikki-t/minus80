"""Class module that represents an email message."""

# Standard library imports
from email.mime.text import MIMEText
from time import sleep
import smtplib
import ssl
import sys

# Local application imports
try:
    from app.mail_data import mail_data
except ModuleNotFoundError:
    from mail_data import mail_data

class Email:
    """Class that represents an email message.

    Attributes
    ----------
        imap : str
            IMAP server used to send mail
        port : int 
            Port to connect to IMAP server on
        context : SSL context
            SSL wrapper to send encrypted email
        password : str
            Google Mail app password
        sender : str
            Email sender
        recipient : str
            Email recipient
        subject : str 
            Subject of email
        body : str
            Body of email
    Methods
    -------
        send_email()
            Sends an email based on self attributes
    """

    def __init__(self, recipient, subject="", body=""):
        """
        Parameters
        ----------
            imap : str
                IMAP server used to send mail
            port : int 
                Port to connect to IMAP server on
            context : SSL context
                SSL wrapper to send encrypted email
            password : str
                Google Mail app password
            sender : str
                Email sender
            recipient : str
                Email recipient
            subject : str 
                Subject of email
            body : str
                Body of email
        """
        self.__imap = mail_data["imap_server"]
        self.__port = mail_data["port"]
        self.__context = ssl.create_default_context()
        self.__password = mail_data["mail_password"]
        self.__sender = mail_data["sender"]
        self.__recipient = recipient
        self.__subject = subject
        self.__body = body

    def set_subject(self, subject):
        """Set subject attribute"""

        self.__subject = subject

    def get_recipient(self):
        """Returns recipient property value"""

        return self.__recipient

    def __str__(self):
        """Returns a string representation of Email object's state"""

        return (
            f"IMAP server: {self.__imap}"
            f"\nPort: {self.__port}"
            f"\nSender: {self.__sender}"
            f"\nRecipient: {self.__recipient}"
            f"\nSubject: {self.__subject}"
            f"\nBody: {self.__body}"
        )

    def send_email(self):
        """Sends email based on object attribute values"""

        # Set up message details
        message = MIMEText(self.__body, "plain")
        message["Subject"] = self.__subject
        message["From"] = self.__sender
        message["To"] = self.__recipient

        try:
            # Create a secure connection and send email
            with smtplib.SMTP_SSL(self.__imap, self.__port, 
                context=self.__context) as smtp_server:
                
                # Login
                smtp_server.login(self.__sender, self.__password)

                # Send mail
                smtp_server.sendmail(self.__sender, self.__recipient, 
                    message.as_string())

        except Exception as error:
            raise Exception(error)

if __name__ == "__main__":
    """Test email functionality"""

    # Define recipient, subject, and body
    try:
        recipient = sys.argv[1]
    except IndexError:
        raise SystemExit("Please enter an email address as a command line " + 
            "argument to send the test to.")
    subject = "Test mail subject"
    body = "Test mail body."
    
    # Create an email object
    email = Email(recipient, subject, body)

    # Send email
    email.send_email()

    print("Email sent.")
