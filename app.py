import os
import socket
import win32event
import win32api
import winerror

# #this hide function help to minimize the console
# def hide():
#     import win32console,win32gui
#     window = win32console.GetConsoleWindow()
#     win32gui.ShowWindow(window,0)
#     return True

# hide()

#For creating app dir
def dir_path():
    home_path = os.path.expanduser("~")
    dir_name = "zlogger"
    dir_path = os.path.join(home_path, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os. chdir(dir_path)
    return dir_path

# check if internet is connected or not
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False



