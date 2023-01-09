
# %%
import time
import socket
import threading
import traceback

from main_setup import main_setup, signal_sender_setup, logger


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
        self.handle_sessions()

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
            param: buffer: The buffer to send

        Return:
            return: n: How many sessions were sent through
        '''
        n = 0
        for session in [e for e in self.sessions if e.is_connected]:
            n += session.send(buffer)
        return n

    def handle_sessions(self):
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
            param: buffer: The buffer to send;
            param: debug: Whether to noise the debug output

        Return:
            return: (int): If the sending was successful, 1 means success, 0 means failure
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


# %%
if __name__ == '__main__':
    logger.info('Session starts')

    server = SocketServer()
    server.start()

    while True:
        inp = input('>> ')

        if not inp:
            continue

        if inp == 'q':
            break

        server.send(inp.encode())

    logger.info('Session stops')
