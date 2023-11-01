from sync_ftp import SyncFtp
from is_connected import is_connected
import os
import time
# from user_name import user_name
def sync():
    home_path = os.path.expanduser("~")
    dir_list = os.listdir(home_path)
    if "zlogger" in dir_list:
        source_path = os.path.join(home_path, "zlogger")
        target_path = "/var/www/html/"

    SYNC = SyncFtp("20.124.217.64", "zlogger", "zlogger")
    
    while True:
        if is_connected() == True:
            print("Internet is available. Syncing..")
            SYNC.send_to_ftp(source_path, target_path)
        else:
            print("No internet! Checking for internet connectivity..")
        time.sleep(50)
