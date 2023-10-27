import socket
# get the user name as identifier
def user_name():
    user_name = str(socket.gethostname())
    return user_name