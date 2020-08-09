# minus80

## Project Overview
Python program for monitoring Minus 80 freezers and sending alert notifications.

The program monitors a specific pin on a Raspberry Pi for a state change and 
alerts an alarm state or recovery based on the voltage applied to the pin. 
The alert sends an email to notify lab members of a potential problem with
their minus80 freezer by parsing a CSV file for the correct recipient based
on the Pi's IP address. If the pin is in an alarm state the program will email
recipients every ten minutes for an hour or until a recovery state is reached
which ever comes first.

The program uses the [RPi.GPIO package](https://pypi.org/project/RPi.GPIO/) 
to monitor pin input and detect edge changes.

The program has a configuration file called `mail_data.py` that allows
one to configure a sender, IT group email, and other authentication data.

If the CSV file fails to be parsed for a recipient the IT team is emailed the
error message to respond appropriately. If there is a network issue the program
attempts to email the IT Team repeatedly every five minutes until the issue
is resolved.

Status, error, and critical messages are logged to the console and to 
`/var/log/syslog`.

## Installation

1. Download minus 80 program from GitHub: You will need to place a zip of the program in the home directory of bmbchem. This repo is currently private and does not support curl or wget commands.
2. Place `minus80` directory in `/usr/local/sbin/` : `drwxr-xr-x 4 bmbchem bmbchem 4096 May 16 19:33 minus80`
2. Install and create virtual environment in `/usr/local/sbin/`owned by `bmbchem`:
```
apt install python3-venv
mkdir /usr/local/sbin/venv && cd /usr/local/sbin/venv
python3 -m venv env
```
4. Change to minus80 directory: `cd /usr/local/sbin/minus80/`
3. Activate virtual environment: `source /usr/local/sbin/venv/env/bin/activate`
4. Install program requirements: `pip3 install -r requirements.txt`
5. Deactivate virtual environment: `(env) $ deactivate`

## Configuration
### mail_data
Configure mail data with the following info to successfully send email:
- IT Group email address
- Sender (the address from which the email will be sent)
- Password for the sender email account
- IMAP server
- Port

### CSV file
COLUMNS: `Freezer Number,Department,PI,Email,MFG,Model Number,Location,Jack Number,IP,Hostname,MAC,Comments`

## Operation
1. Activate virtual environment: `source /usr/local/sbin/venv/env/bin/activate`
2. Run: `python3 /usr/local/sbin/minus80/minus80_main.py`

Note: Runs forever; Keyboard interrupt is not processed as RPi.GPIO.wait_for_edge function blocks interrupt signal. Use `systemctl` to manage `minus80.service`.

## File List
```.
├── app
│   ├── Board.py
│   ├── Email.py
│   ├── Event.py
│   ├── FreezerData.py
│   ├── freezer_info.csv
│   ├── __init__.py
│   └── mail_data.py
├── __init__.py
├── LICENSE
├── minus80_main.py
├── README.md
├── requirements.txt
├── setup.py
└── tests
    ├── ErrorAfterCall.py
    ├── freezer_test.csv
    ├── __init__.py
    ├── test_board.py
    ├── test_email.py
    ├── test_event.py
    ├── test_freezer_data.py
    └── test_integration.py
```

## Test
Tests are contained in `tests/` and are discoverable by unittest:
1. Activate virtual environment: `source /usr/local/sbin/venv/env/bin/activate`
2. `cd /usr/local/sbin/minus80/`
3. Run: `python3 -m unittest discover`
4. Deactivate virtual environment: `(env) $ deactivate`

To test email functionality you can run the Email class: 
1. Activate virtual environment: `source /usr/local/sbin/venv/env/bin/activate`
3. Run: `python3 /usr/local/sbin/minus80/app/Email.py [email address to send test to]`
4. Deactivate virtual environment: `(env) $ deactivate`

## Contact information
Developer: Nikki Tebaldi

Contact: ntebaldi@umass.edu

## Changelog
Version 2.0: Revamp of minus80 script using object-oriented programming.
