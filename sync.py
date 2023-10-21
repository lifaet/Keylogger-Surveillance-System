##############################################################################
from dirsync import sync
import ftplib
import os
# Connect to the FTP server and login
ftp = ftplib.FTP("ftp://zroot@20.124.217.64")
ftp.login("user_name", "password")
home_path = os.path.expanduser("~")
dir_name = "zlogger"
# Define the source and target paths
source_path = os.path.join(home_path, dir_name)
target_path = "/remote/folder/path"

# Sync the local folder with the remote folder using the "copy" option
sync(source_path, target_path, "copy", ftp=ftp)

# # Close the FTP connection
# ftp.quit()

# #############################################################################
# import os
# import subprocess
# import watchdog.events
# import watchdog.observers

# # Define your git user_name, personal access token, and repository name
# user_name = "lifaet"
# token = "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"
# repo_name = "zlogger"
# # Define your local and remote repository paths
# home_path = os.path.expanduser("~")
# dir_name = "zlogger"
# local_path = os.path.join(home_path, dir_name)
# remote_path = f"https://github.com/{user_name}/{repo_name}"

# # Check if your local folder already has a .git subfolder, which indicates that it is already a git repository
# if not os.path.exists(os.path.join(local_path, '.git')):
#     # If not, initialize it as a git repository
#     subprocess.run(["git", "init", local_path])

# # Set the remote URL of your GitHub repository as the origin for your local repository
# subprocess.run(["git", "remote", "add", "origin", remote_path])

# # Optionally, pull the existing files from your remote repository to your local repository, if you want to sync them
# subprocess.run(["git", "pull", "origin", "master"])

# # Define a handler class that inherits from FileSystemEventHandler
# class GitHandler(watchdog.events.FileSystemEventHandler):
#     # Define a method that is called when a file or directory is created
#     def on_created(self, event):
#         # Change directory to your local repository
#         subprocess.run(["cd", local_path])
#         # Add all files to the staging area
#         subprocess.run(["git", "add", "."])
#         # Commit your changes with a message
#         subprocess.run(["git", "commit", "-m", "New file created"])
#         # Push your changes to your remote repository using your user_name and token
#         subprocess.run(["git", "push", f"https://{user_name}:{token}@{remote_path}"])

# # Create an observer object
# observer = watchdog.observers.Observer()

# # Create a handler object
# handler = GitHandler()

# # Schedule the observer to watch the local directory for changes
# observer.schedule(handler, local_path, recursive=True)

# # Start the observer
# observer.start()
