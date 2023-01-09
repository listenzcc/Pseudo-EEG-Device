
# %%
import time
import socket
import threading
import traceback

from main_setup import signal_sender_setup, logger

# %%


class SocketClient(object):
    ''' Socket client for Pseudo EEG Device '''

    def __init__(self):
        self.host = signal_sender_setup['host']
        self.port = signal_sender_setup['port']

    def connect(self):
        ''' Connect to the server '''
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.receive()
        logger.info('Connected to {}:{}'.format(self.host, self.port))

    def receive(self):
        buffer = self.client.recv(20)
        print(buffer)


# %%
if __name__ == '__main__':
    client = SocketClient()
    client.connect()

    while True:
        inp = input('>> ')

        if inp == 'q':
            break

        client.receive()

    input('Press Enter to quit')
    pass
