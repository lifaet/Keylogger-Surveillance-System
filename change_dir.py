import os
from user_name import user_name
#For creating app dir
def dir_path():
    home_path = os.path.expanduser("~")
    dir_name = "zlogger"

    dir_path = os.path.join(home_path, dir_name, user_name())
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os. chdir(dir_path)
    return dir_path