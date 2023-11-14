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
        self.localfolder = localfolder
        self.remotefolder = remotefolder
        os.chdir(self.localfolder)
        with ftputil.FTPHost(self.host, self.login, self.password) as ftp_host:
            ftp_host.synchronize_times()
            ftp_host.chdir(self.remotefolder)
            for root, dirs, files in os.walk("./"):
                for d in dirs:
                    if platform.system() == "Windows":
                        newdir = os.path.join(root, d).replace("\\", "/")
                    else:
                        newdir = os.path.join(root, d)

                    if ftp_host.path.isdir(newdir) ==False:
                        ftp_host.mkdir(newdir)

                for file in files:
                    if platform.system() == "Windows":
                        newfile = os.path.join(root, file).replace("\\", "/")
                    else:
                        newfile = os.path.join(root, file)
                    ftp_host.upload_if_newer(newfile, newfile)

