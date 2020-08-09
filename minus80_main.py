"""Program that monitors a Raspberry Pi attached to a minus 80 freezer.

Functions
---------
    monitor(): Creates Board object to watch the state of an input pin.
"""

# Local application imports
from app.Board import Board

PIN = 11

def monitor():
    """Creates a Board object to monitor the state of an input pin."""

    # Create a Board object
    board = Board(PIN)

    # Log Board IP and hostname
    board.get_board_logger().info("IP: %s | Hostname: %s", \
        str(board.get_ip()), str(board.get_hostname()))
    
    # Setup board: Mode and input pin
    board.setup()

    # Monitor board for events
    board.monitor()

if __name__ == "__main__":
    monitor()
