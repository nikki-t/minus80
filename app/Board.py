"""Class module that represents a Raspberry Pi board with GPIO pins.
"""

# Standard library imports
from datetime import datetime
from datetime import timedelta
import logging
from logging.handlers import SysLogHandler
import netifaces
from threading import Thread
import socket
from time import sleep

# Third part imports
import RPi.GPIO as GPIO

# Local application imports
from app.Event import Event

class Board:
    """Class that represents a Raspberry Pi board with GPIO pins.

    Attributes
    ----------
        pin : int
            Pin number to monitor
        hostname : str
            Hostname of the Raspberry Pi
        ip : str
            IP of the Raspberry Pi
        input_status : int
            Pin input value
        board_logger : Logger
            Logger object to log to console
    Methods
    -------
        get_hostname()
            Returns hostname of Raspberry Pi
        get_ip()
            Returns IP address of Raspberry Pi
        get_board_logger()
            Creates, configures and returns a Logger object
        set_up()
            Sets up and initializes the GPIO board
        monitor()
            Monitors GPIO board to detect for changes on pin
        alert()
            Creates a new Event object to send appropriate communications
        check_alert()
            Loops for an hour and if alert status is error; Alerts 
            every ten minutes
    """

    def __init__(self, pin):
        """
        Parameters
        ---------
        pin : int
            Pin number to monitor
        """
        self.__pin = pin
        self.__hostname = socket.gethostname()
        self.__ip = netifaces.ifaddresses("eth0")[2][0]["addr"]
        self.__input_status = None    # Set to None as monitor() will initialize
        self.__board_logger = self.__init_board_logger()

    def __init_board_logger(self):
        """Creates, configures, and returns a Logger object."""
        
        # Create a Logger object and set log level
        board_logger = logging.getLogger(__name__)
        board_logger.setLevel(logging.DEBUG)

        # Create a handler to console and set level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create a formatter and add it to the handler
        console_format = logging.Formatter("%(asctime)s - %(threadName)s - "
            + "%(module)s - %(levelname)s : %(message)s")
        console_handler.setFormatter(console_format)

        # Create a handler for syslog and set level
        syslog_handler = SysLogHandler("/dev/log")
        syslog_handler.setLevel(logging.INFO)

        # Create a formatter and add it to handler
        syslog_format = logging.Formatter("%(asctime)s - %(threadName)s - "
           + "%(module)s -  %(levelname)s : %(message)s")
        syslog_handler.setFormatter(syslog_format)

        # Add handlers to logger
        board_logger.addHandler(console_handler)
        board_logger.addHandler(syslog_handler)

        # Return logger
        return board_logger
    
    def get_hostname(self):
        """Return hostname"""
        
        return self.__hostname
    
    def get_ip(self):
        """Return IP address"""
        
        return self.__ip
    
    def get_input_status(self):
        """Return current input status of the board object"""
        
        return self.__input_status

    def set_input_status(self, input_status):
        """Set the input status of the board object"""
        
        self.__input_status = input_status
    
    def get_board_logger(self):
        """Returns board_logger instance"""
        
        return self.__board_logger
    
    def __str__(self):
        """Returns a string representation of Board object's state"""
        
        return (
            f"Pin: {self.__pin}"
            f"\nHostname: {self.get_hostname()}"
            f"\nIP: {self.get_ip()}"
            f"\nInput status: {self.get_input_status()}"
            f"\nLogger name: {self.get_board_logger().name}"
        )
        
    def setup(self):
        """Sets the Raspberry Pi GPIO board mode and establishes pin as input in 
        order to monitor pin for changes.
        """
        
        # Board refers to the P1 header of the Raspberry Pi board
        GPIO.setmode(GPIO.BOARD)

        # Set up pin as an input with a pull up resistor to 3.3V
        GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def monitor(self):
        """Monitors pin for changes. 
        
        If a change is detected, spawn a new thread and alert via an Event
        object. Function is inifinite and never ends.
        """

        # Log beginning of process
        board_logger = self.get_board_logger()
        board_logger.info("Beginning monitor of input for pin %s.", \
            self.__pin)
 
        # Set input status of pin for board object
        self.set_input_status(GPIO.input(self.__pin))
        status = "ALARM" if self.get_input_status() else "RECOVERY"
        board_logger.info("Initital status: %s", status)

        # Deal with an error status upon power failure
        if self.get_input_status() == 1: self.initiate_event()

        # Monitor pin until KeyBoardInterrupt is detected
        while True:

            # Log monitoring
            board_logger.info("Monitoring for pin changes...")
            
            # Wait for a change in pin status
            GPIO.wait_for_edge(self.__pin, GPIO.BOTH)

            sleep(0.005) #debounce for 5ms

            if self.get_input_status() != GPIO.input(self.__pin):
                
                # Set input status of pin
                self.set_input_status(GPIO.input(self.__pin))

                # Initiate event
                self.initiate_event()

    def initiate_event(self):
        """Creates a new Thread object with the alert function as a target. """

        # Determine and log status change
        status = "ALARM; initiating alarm event." \
            if self.get_input_status() else "RECOVERY."
        
        self.get_board_logger().info("Pin input status changed to %s", \
            status)

        # Create thread to handle event alert
        event_thread = Thread(target=self.alert, args=(), \
            name="EventThread")
        
        event_thread.start()

    def alert(self):
        """Creates an Event object to send appropriate alerts. """

        # Get board logger
        board_logger = self.get_board_logger()

        # Create new Event object to handle event communication
        event = Event(datetime.now(), self.get_input_status())
        
        event.alert(self.__ip, board_logger)

        if (self.get_input_status() == 1):
            
            board_logger.info("Alarm state active; starting check alert " 
                + "cycle for 6 cycles.")
            
            self.check_alert(event)

    def check_alert(self, event):
        """If input pin signifies an alert, the program will keep alerting every
        ten minutes for an hour."""
        
        # Get board logger
        board_logger = self.get_board_logger()

        # Loop for an hour and continue to alert every ten minutes 
        current_time = datetime.now()
        end_time = current_time + timedelta(0, 60)
        # end_time = current_time + timedelta(hours=1)

        alarm_counter = 0
        while current_time < end_time:
            # Sleep for 10 minutes
            sleep(10);
            #sleep(600);

            # Prevent race condition between Board input_status and check_alert 
            if GPIO.input(self.__pin) == 1:

                # Log alarm cycle
                alarm_counter += 1
                board_logger.info("Alarm Cycle #%s: Initiating event " 
                    + "alert.", str(alarm_counter))

                # Call Event object's alert method
                event.alert(self.__ip, board_logger)

                # Get current time
                current_time = datetime.now()
            
            else:
                # Input status is 0 indicating recovery; Break out of loop and 
                # return to main thread       
                board_logger.info("Alarm state recovery.")   
                break
        
        # End of alert cycle; Return to main thread
        status = "ALARM" if self.get_input_status() else "RECOVERY"
        board_logger.info("End check alarm cycle. Current pin input "
            + "status is %s.", status)