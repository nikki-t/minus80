"""Class module that represents freezer data obtained from CSV file."""

# Standard library imports
import csv
import pathlib

class FreezerData:
    """
    Class that represents freezer data obtained from CSV file.

    Attributes
    ----------
        csv_file : Path
            File path location of file that contains freezer data
        data : dictionary
            Dictionary of freezer data
    Methods
    -------
        parse_csv(ip): Parse CSV file and determines appropriate freezer data
    """

    def __init__(self, csv_file = pathlib.Path("/home/pi/minus80/app/freezer_info.csv")):

        self.__csv_file = csv_file
        self.__data = {}
    
    def get_data(self):
        """ Returns Freezer Data data attribute"""
        
        return self.__data
    
    def set_data(self, ordered_dict):
        """ Sets Freezer Data dat attribute"""
        
        self.__data = ordered_dict
    
    def parse_csv(self, ip):
        """Parses CSV file and populates data attribute with appropriate freezer 
        data based on ip parameter.

        Parameters:
            ip : str
                IP of the Raspberry Pi
        """

        # Open CSV file and read in data as a dictionary
        try:
            with open(self.__csv_file, newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if row["IP"] == ip:
                        self.__data = row
                        break
        except FileNotFoundError:
            raise