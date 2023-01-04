
# %%
import time
import socket
import threading
import traceback

from main_setup import server_setup, logger

# %%


class SocketClient(object):
    ''' Socket client for Pseudo EEG Device '''

    def __init__(self):
        self.host = server_setup['host']
        self.port = server_setup['port']

    def connect(self):
        ''' Connect to the server '''
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.receive()
        logger.info('Connected to {}:{}'.format(self.host, self.port))

    def receive(self):
        buffer = self.client.recv(20)
        print(buffer)

    # def receive(self):
    #     ''' Keep receiving the data from the server '''

    #     self.keep_receiving = True

    #     def _loop():
    #         logger.info('Start receiving loop')

    #         try:
    #             while self.keep_receiving:
    #                 buffer = self.client.recv(1024)
    #                 if buffer.startswith(b'data'):
    #                     output = decode_header(buffer[:20])
    #                     n = output['n']
    #                     k = output['k']
    #                     q = output['q']

    #                     logger.debug('Expecting package length: {}'.format(k))
    #                     while k + 20 > len(buffer):
    #                         buffer += self.client.recv(min(1024,
    #                                                        k+20 - len(buffer)))

    #                     if not k + 20 == len(buffer):
    #                         logger.error(
    #                             'Received unexpected package with wrong length')
    #                         break

    #                     package = buffer[20:]
    #                     data = decode_package(package)
    #                     print(n, q, data.shape)

    #         except ConnectionAbortedError as err:
    #             logger.error('ConnectionAbortedError occurred')

    #         except Exception as err:
    #             logger.error('Unknown error occurs {}'.format(err))
    #             logger.error(traceback.format_exc())

    #         self.keep_receiving = False

    #         logger.info('Stop receiving loop')

    #     t = threading.Thread(target=_loop, daemon=True)
    #     t.start()


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
