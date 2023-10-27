import os
import socket
import win32event
import win32api
import winerror

#For creating app dir
def dir_path():
    home_path = os.path.expanduser("~")
    dir_name = "zlogger"
    dir_path = os.path.join(home_path, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os. chdir(dir_path)
    return dir_path

# #disallowing multiple instance
# def disable_multiple_instance():
#     mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
#     if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
#         mutex = None
#         print ("Multiple Instance not Allowed")
#         exit(0)
#     x=''
#     data=''
#     count=0

# check if internet is connected or not
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False



