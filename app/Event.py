"""Class module that represents an Event that occurs when a change is detected on a
GPIO pin.
"""

# Standard library imports
import datetime
from time import sleep

# Local application imports
from app.Email import Email
from app.FreezerData import FreezerData
from app.mail_data import mail_data

class Event:
    """Class to represent an Event that gets trigger when a change is detected on a
    GPIO pin.

    Attributes
    ----------
        event_time : datetime
            Time of event
        status : str
            Type of event that has occured, either ALARM or RECOVERY
    Methods
    -------
        alert(ip, board_logger)
            Alerts the appropriate parties that an event has happened
        handle_error(error, error_message, board_logger)
            Logs error and then attempts to email IT Team error message
        notify_recipients(freezer_data, success_message, board_logger)
            Sends email to appropriate recipients to notify event status
        handle_email_error(email, board_logger)
            Tries to send email every 5 minutes
    """

    def __init__(self, event_time, event_type):
        """
        Parameters
        ----------
            event_time : datetime
                Time of event
            status : str
                Type of event that has occured, either ALARM or RECOVERY
        """
        
        self.__event_time = event_time
        self.__status = "ALARM" if event_type else "RECOVERY"
    
    def get_event_time(self):
        """Returns event time"""
        
        return self.__event_time
    
    def get_event_status(self):
        """Returns event status"""
        
        return self.__status
    
    def set_event_time(self, event_time):
        """Sets event time"""
        
        self.__event_time = event_time

    def alert(self, ip, board_logger):
        """Alerts the appropriate parties that an event has happened.

        Parameters
        ----------
            board_logger : Logger
                Logger object to log to console
            ip : str
                IP of the Raspberry Pi

        Returns
        -------
            self.alerted : bool
                Whether event was successfully alerted
        """
        
        # Create new FreezerData object
        freezer_data = FreezerData()
        
        # Parse CSV file
        try:
            freezer_data.parse_csv(ip)
            if (freezer_data.get_data() == {}):
                raise Exception("CSV data returned empty.")
            else:
                parsed = True
        except Exception as error:
            # Error has been caught; log the error and email IT team
            parsed = False
            error_message = "Failed to parse CSV file"
            self.handle_error(error, error_message, board_logger)

        # Notify recipients of minus 80 status
        if (parsed):
            success_message = "Parsed CSV file for freezer data"
            self.notify_recipients(freezer_data, success_message, board_logger)

    def notify_recipients(self, freezer_data, success_message, board_logger):
        """Sends email to appropriate recipients to notify event status.

        Precondition: Successfully parsed FreezerData csv.
        
        Parameters
        ----------
            freezer_data : FreezerData
                FreezerData object
            success_message : str
                Message that indicates success
            board_logger: Logger
                Logger object to log to console
        """

        board_logger.info("%s.", success_message)
        data = freezer_data.get_data()

        # Create string to represent event data
        date = self.get_event_time().strftime('%m/%d/%Y')
        time = self.get_event_time().strftime('%H:%M:%S')
        location = data['Location']

        # Email details
        if (self.get_event_status() == "ALARM"):
            subject = (
                f"!!! -80 ALARM !!! Problem detected on " 
                f"{date} at {time} in {location}"
            )
            
            body = (
                f"ALARM event detected on "
                f"{date} at {time}. "
                f"\nThere is a problem with the -80 in {location}."
            )
        else:
            subject = (
                f"!!! -80 RECOVERY !!! Recovery detected on " 
                f"{date} at {time} in {location}"
            )

            body = (
                f"RECOVERY event detected on "
                f"{date} at {time} for minus 80 in "
                f"{location}."
            )
        recipient = data["Email"]

        # Create Email object and try to send mail
        try:
            email = Email(recipient, subject, body)
            email.send_email()
            board_logger.info("Email sent to %s.", email.get_recipient())
        except Exception as error:
            # Create error message
            error_message = (f"!!! -80 ALERT !!! Failure to email "
                f"{email.get_recipient()}")
            self.handle_error(error, error_message, board_logger)

    def handle_error(self, error, error_message, board_logger):
        """Logs error and then attempts to email IT Team error message.

        Precondition: Failed to send email to FreezerData recipients.
        
        Parameters
        ----------
            error : Exception
                Exception object
            error_message : str
                String that indicates error that occured
            board_logger: Logger
                Logger object to log to console
        """
        
        board_logger.error("%s.", error_message)
        board_logger.error("DETAILS: %s", error)

        # Email IT team
        subject = f"!!! -80 ALERT !!! {error_message}"
        body = (
            f"Minus 80 alarm status: {self.get_event_status()}. "
            f"\nEvent time: {self.get_event_time().strftime('%d/%m/%Y %H:%M:%S')}"
            f"\nError: {error_message}."
            f"\nCheck syslog for further error details."
        )

        # Create new Email object and try to send email to IT team
        try:
            email = Email(mail_data["it_email"], subject, body)
            email.send_email()
            board_logger.info("Email sent to %s.", email.get_recipient())
        except Exception as error:
            # Add to error message
            error_message += " AND email IT team"
                       
            # Failed to email, log the error
            board_logger.critical("ERROR: %s.", error_message)
            board_logger.critical("Attempting to email IT team every 5 " +
                "minutes until successful.")
            board_logger.critical("DETAILS: %s", error)
            
            # Try to email every 5 minutes
            email.set_subject(error_message)
            self.handle_email_error(email, board_logger)

    def handle_email_error(self, email, board_logger):
        """Tries to send email every 5 minutes.

        Precondition: Failed to send email to FreezerData recipients and to IT 
        team.
        
        Parameters
        ----------
            email : Email
                Email object
            board_logger: Logger
                Logger object to log to console
        """

        # Flag to track if email is sent
        email_sent = False
        failure_count = 0
        
        while not email_sent:
            # Sleep for 5 minutes
            sleep(5)
            try:
                email.send_email()
                board_logger.info("Email sent to %s.", email.get_recipient())
                email_sent = True
            except Exception as error:
                failure_count += 1
                board_logger.critical("Failure attempt #%i", failure_count)
                board_logger.critical("Failure to send email to %s.", 
                    email.get_recipient())
                board_logger.critical("ERROR DETAILS: %s", error)
                email_sent = False