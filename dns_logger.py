#library
import netifaces
import winreg
import logging
import scapy.all as scapy
from current_time import current_time
from user_name import user_name

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