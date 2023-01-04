'''
The signal sender of EEG device.
'''

# %%
import time
import struct
import traceback
import threading
import numpy as np

from main_setup import main_setup, logger
from coding_toolbox import generate_package, encode_header, decode_header


# %%


class EEG_Device_Signal_Sender(object):
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

    def keep_sending_buffer(self):
        '''
        keep empty the buffer by sending the elements
        '''
        def _send(header, code):
            '''
            Send the header + code
            '''
            output = decode_header(header)
            print(output, len(code))

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

    def keep_fill_buffer(self, interval=main_setup['interval']):
        '''
        Keep fill the buffer at the fixed rate

        Args:
            param: interval: The interval between the filling events in milliseconds
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

    edss = EEG_Device_Signal_Sender()
    edss.keep_fill_buffer()
    edss.keep_sending_buffer()

    input('Press enter to quit')

# %%
