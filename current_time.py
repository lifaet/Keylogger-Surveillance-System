import datetime
# get the current date and time as a string
def current_time():
    current_time = datetime.datetime.now().strftime('-%Y-%m-%d-%H-%M-%S')
    return current_time