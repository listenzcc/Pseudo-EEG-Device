'''
File: signal_sender.py
Author: listenzcc
Date: 2023-01-04

The signal sender of Pseudo EEG device.
'''

# %%
import time
import socket
import threading
import traceback

from main_setup import main_setup, signal_sender_setup, logger
from coding_toolbox import generate_package, encode_header, decode_header


# %%

class SocketServer(object):
    '''
    Socket server as the EEG signal sender
    '''

    def __init__(self):
        self.host = signal_sender_setup['host']
        self.port = signal_sender_setup['port']
        self.sessions = []

    def start(self):
        ''' Start the server '''
        self.bind()
        self.handling_sessions()

    def bind(self):
        '''
        Bind the server with given host and port
        '''
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        self.server = server
        self.server.listen(1)
        logger.info('Server listening on {}:{}'.format(self.host, self.port))

    def check_sessions(self):
        ''' Remove invalid sessions and list the valid sessions '''
        self.sessions = [e for e in self.sessions if e.is_connected]
        logger.debug('Found {} sessions'.format(len(self.sessions)))
        return self.sessions

    def send(self, buffer):
        '''
        Send the buffer to all the sessions 

        Args:
            :param: buffer: The buffer to send

        Return:
            :return: n: How many sessions were sent through
        '''
        n = 0
        for session in [e for e in self.sessions if e.is_connected]:
            n += session.send(buffer)
        return n

    def handling_sessions(self):
        '''
        Handling the incoming sessions in a separate threading.
        '''
        self.keep_alive = True

        def _loop():
            logger.debug('Handling sessions starts')
            while self.keep_alive:
                client, address = self.server.accept()
                session = SocketSession(client=client, address=address)
                self.sessions.append(session)
                self.check_sessions()
            logger.debug('Handling sessions stops')

        t = threading.Thread(target=_loop, daemon=True)
        t.start()


class SocketSession(object):
    '''
    The socket session of the incoming client.
    The session is created and maintained by SocketServer.
    '''

    def __init__(self, client, address):
        self.client = client
        self.address = address
        self.buffer_size = 1024
        self.start()

    def start(self):
        ''' Start listening the client '''
        t = threading.Thread(target=self.listen, daemon=True)
        t.start()
        logger.error('Client started {}'.format(self.client))

    def close(self):
        ''' Close the connection with the client '''
        self.is_connected = False
        logger.error('Client closed {}'.format(self.client))

    def send(self, buffer, debug=False):
        '''
        Send bytes to the client

        Args:
            :param: buffer: The buffer to send;
            :param: debug: Whether to noise the debug output

        Return:
            :return: (int): If the sending was successful, 1 means success, 0 means failure
        '''
        try:
            self.client.sendall(buffer)
            if debug:
                logger.debug('Client sent {} bytes, {}'.format(
                    len(buffer), buffer[:20]))
            return 1
        except Exception as err:
            logger.error('Client sent {} bytes, {}'.format(
                len(buffer), buffer[:20]))
            self.close()
            return 0

    def listen(self):
        ''' Handle the message from the client'''
        self.is_connected = True
        while self.is_connected:
            try:
                buffer = self.client.recv(self.buffer_size)
                logger.debug('Received {} bytes'.format(len(buffer)))

                if len(buffer) == 0:
                    break

            except ConnectionAbortedError as err:
                logger.error('Connection reset error: {}'.format(err))
                break

            except Exception as err:
                logger.error('Unknown error: {}'.format(err))
                logger.error(traceback.format_exec())
                break

        self.close()


class EEG_Pseudo_Device(object):
    '''
    Automatic signal server for Pseudo EEG device
    '''

    def __init__(self):
        self.reset()
        pass

    def reset(self):
        '''
        Reset the buffer and package idx
        '''
        self.buffer = []
        self.n = 0
        self.keep_filling = False
        self.keep_sending = False
        logger.debug('Dataset is reset')

    def keep_sending_buffer(self, server=None):
        '''
        keep empty the buffer by sending the elements
        '''
        def _send(header, code):
            '''
            Send the header + code

            Args:
                :param: header: The header to send;
                :param: code: The code to send

            Return:
                :return: n: How many sessions were sent thought
            '''
            output = decode_header(header)
            n = -1
            if server is not None:
                n = server.send(header + code)

            if n > 0:
                print('Sent to {} clients'.format(n), output, len(code))
            else:
                print('Not sent', output, len(code))

            return n

        def _loop():
            '''
            Keep detecting the buffer and sending the elements
            '''
            self.keep_sending = True
            while self.keep_sending:
                if len(self.buffer) > 0:
                    n, k, q, code = self.buffer.pop(0)
                    header = encode_header(n, k, q)
                    _send(header, code)

        t = threading.Thread(target=_loop, daemon=True)
        t.start()

    def keep_filling_buffer(self, interval=main_setup['interval']):
        '''
        Keep fill the buffer at the fixed rate

        Args:
            :param: interval: The interval between the filling events in milliseconds
        '''

        def _fill_buffer():
            '''
            Fill the buffer with generated package
            '''
            n, k, q, code, data = generate_package(self.n)
            self.n += 1
            self.buffer.append((n, k, q, code))

        def _loop():
            '''
            Fill the buffer in a loop until the keep_filling symbol is reset
            '''
            self.keep_filling = True

            t0 = time.time()
            n0 = self.n
            logger.debug('Start _keep_fill_buffer.')
            while self.keep_filling:
                if (time.time() - t0) * 1000 < (self.n - n0) * interval:
                    continue
                _fill_buffer()

            logger.debug('Stop _keep_fill_buffer.')

            return

        self.reset()
        t = threading.Thread(target=_loop, daemon=True)
        t.start()


# %%
if __name__ == '__main__':
    logger.info('Session starts')

    server = SocketServer()
    server.start()

    eeg_pd = EEG_Pseudo_Device()
    eeg_pd.keep_filling_buffer()
    eeg_pd.keep_sending_buffer(server)

    input('Press enter to quit')

# %%
