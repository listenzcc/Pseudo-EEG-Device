'''
File: data_center.py
Author: listenzcc
Date: 2023-01-04

The Data Center of Pseudo EEG Device
'''

# %%
import time
import socket
import threading
import traceback
import pandas as pd

from main_setup import signal_sender_setup, logger
from coding_toolbox import decode_header, decode_body

# %%


class DataSet(object):
    ''' Main dataset of the Pseudo EEG Device Signal '''

    def __init__(self):
        self.reset()

    def reset(self):
        ''' Reset the dataset '''
        self.dataset = []

    def append(self, n, q, q2, data):
        '''
        Append the signal into the dataset

        Args:
            param: n: The count of the signal segment;
            param: q: The timestamp of the signal segment;
            param: q2: The timestamp of receiving the signal segment
            param: data: The 2D array of the signal segment
        '''
        self.dataset.append((n, q, q2, data))

    def dataframe(self):
        '''
        Convert the dataset into the dataframe

        Return:
            return: df: The dataframe of the dataset
        '''
        df = pd.DataFrame(self.dataset, columns=['n', 'q', 'q2', 'data'])
        df['diff'] = df['q2'] - df['q']

        df = df[['n', 'diff', 'q', 'q2', 'data']]
        return df


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
                        output = decode_header(buffer[:20])
                        n = output['n']
                        k = output['k']
                        q = output['q']

                        logger.debug('Expecting package length: {}'.format(k))
                        while k + 20 > len(buffer):
                            buffer += self.client.recv(min(1024,
                                                           k+20 - len(buffer)))

                        if not k + 20 == len(buffer):
                            logger.error(
                                'Received unexpected package with wrong length')
                            break

                        package = buffer[20:]
                        q2 = time.time()
                        data = decode_body(package)
                        if dataset is not None:
                            dataset.append(n, q, q2, data)
                        print(n, q, q2, data.shape)

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
    dataset = DataSet()

    client = SocketClient()
    client.connect()

    client.receiving(dataset)

    input('Press Enter to quit')

    print(dataset.dataframe())
    pass
