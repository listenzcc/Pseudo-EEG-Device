'''
File: data_center.py
Author: listenzcc
Date: 2023-01-04

The Data Center of Pseudo EEG Device
'''

# %%
import json
import time
import socket
import threading
import traceback
import pandas as pd

import asyncio
import websockets

from main_setup import main_setup, signal_sender_setup, data_center_setup, logger
from coding_toolbox import decode_header, decode_body
from eeg_data_set import DataSet

# %%
dataset = DataSet()

# %%


class WebsocketServer(object):
    def __init__(self):
        pass

    async def handle(self, websocket, path):
        '''
        Handle message from the client, it is an async function.

        Args:
            :param: websocket: The websocket connection;
            :param: path: The request path.
        '''
        def _send(bytes):
            return websocket.send(bytes)

        logger.debug('Received message: {}'.format(path))

        msg = await websocket.recv()

        df = dataset.get_latest(int(msg))

        await _send(df.to_json())

        return

    def start(self, host=None, port=None):
        '''
        Start websocket server, it is an async function.

        Args:
            :param: host: The hostname of the websocket server;
            :param: port: The port of the websocket server.
        '''
        host = data_center_setup['host']
        port = data_center_setup['port']
        async_server = websockets.serve(self.handle, host, port)
        asyncio.get_event_loop().run_until_complete(async_server)
        asyncio.get_event_loop().run_forever()


# %%

HEADER_LENGTH = main_setup['header_length']


class SocketClient(object):
    ''' Socket client for Pseudo EEG Device '''

    def __init__(self):
        self.host = signal_sender_setup['host']
        self.port = signal_sender_setup['port']

    def connect(self):
        ''' Connect to the server '''
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        logger.info('Connected to {}:{}'.format(self.host, self.port))

    def receiving(self, dataset=None):
        '''
        Keep receiving the data from the server

        Args:
            param: dataset: The dataset restoring the data
        '''

        self.keep_receiving = True

        def _loop():
            logger.info('Start receiving loop')

            try:
                while self.keep_receiving:
                    buffer = self.client.recv(80)
                    if buffer.startswith(b'data'):
                        output = decode_header(
                            buffer[:HEADER_LENGTH])
                        n = output['n']
                        k = output['k']
                        q = output['q']

                        logger.debug('Expecting package length: {}'.format(k))
                        while k + HEADER_LENGTH > len(buffer):
                            buffer += self.client.recv(min(1024,
                                                           k+HEADER_LENGTH - len(buffer)))

                        if not k + HEADER_LENGTH == len(buffer):
                            logger.error(
                                'Received unexpected package with wrong length')
                            break

                        package = buffer[HEADER_LENGTH:]
                        q2 = time.time()
                        data = decode_body(package)
                        if dataset is not None:
                            dataset.append(n, q, q2, data)
                        print(n, q, q2, data.shape, data[0][0])

            except ConnectionAbortedError as err:
                logger.error('ConnectionAbortedError occurred')

            except Exception as err:
                logger.error('Unknown error occurs {}'.format(err))
                logger.error(traceback.format_exc())

            self.keep_receiving = False

            logger.info('Stop receiving loop')

        t = threading.Thread(target=_loop, daemon=True)
        t.start()


# %%
if __name__ == '__main__':
    try:
        client = SocketClient()
        client.connect()
        client.receiving(dataset)
    except:
        print('!!! Can not connect to server !!!')

    ws = WebsocketServer()
    ws.start()

    input('Press Enter to quit')

    print(dataset.get_latest())
    pass
