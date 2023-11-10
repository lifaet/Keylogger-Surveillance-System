import os
import platform
import ftputil

class SyncFtp:

    def __init__(self, host, login, password):
        self.host = host
        self.login = login
        self.password = password
        self.localfolder = "./"
        self.remotefolder = "./"
        self.label = 15
        self.path = 50

    def send_to_ftp(self, localfolder, remotefolder):
        print("LOCAL -> FTP".ljust(self.label, " "))
        self.localfolder = localfolder
        self.remotefolder = remotefolder
        os.chdir(self.localfolder)
        with ftputil.FTPHost(self.host, self.login, self.password) as ftp_host:
            ftp_host.synchronize_times()
            ftp_host.chdir(self.remotefolder)
            print("PLATFORM  -> "+ platform.system())
            for root, dirs, files in os.walk("./"):
                for d in dirs:
                    if platform.system() == "Windows":
                        newdir = os.path.join(root, d).replace("\\", "/")
                    else:
                        newdir = os.path.join(root, d)
                    try:
                        if ftp_host.path.isdir(newdir):
                            print("Directory -> " + newdir + "    already exists")
                        else:
                            ftp_host.mkdir(newdir)
                            print("Directory -> " + newdir + "    was created")
                    except ftputil.error.FTPError as exc:
                        print(exc)
                        print("Error Creating directory " + newdir)

                for file in files:
                    if platform.system() == "Windows":
                        newfile = os.path.join(root, file).replace("\\", "/")
                    else:
                        newfile = os.path.join(root, file)
                    try:
                        uploaded = ftp_host.upload_if_newer(newfile, newfile)
                        if uploaded is True:
                            print("File      -> " + newfile + "    was updated")
                        else:
                            print("File      -> " + newfile + "    is up-to-date")
                    except ftputil.error.FTPError as exc:
                        print(exc)
                        print("Error at sending file " + newfile)
