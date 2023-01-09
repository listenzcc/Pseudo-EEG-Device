
# %%
import time
import struct
import numpy as np

from main_setup import main_setup, logger

# %%
channels = main_setup['channels']
interval = main_setup['interval']
sample_rate = main_setup['sample_rate']
data_length = int(interval / 1000 * sample_rate)

# %%

'''
Header encoding and decoding
'''


def encode_header(n, k, q):
    '''
    Encode the header based on n, k, q

    Args:
        param: n: the package id n;
        param: k: The length of the bytes;
        param: q: The time stamp of the package;

    Return:
        return: The encoded header
    '''
    segments = [
        struct.pack('8s', b'data'),
        struct.pack('>H', n),
        struct.pack('>H', k),
        struct.pack('<d', q)
    ]
    return b''.join(segments)


def decode_header(code):
    '''
    Decode the header code

    Args:
        param: code: The given header code;

    Return:
        return: output: The dict contains:
                        s: The leading string;
                        n: the package id n;
                        k: The length of the bytes;
                        q: The time stamp of the package;
    '''
    if not len(code) == 20:
        logger.error(
            'Invalid header code, expected 20 bytes, but received {} bytes'.format(len(code)))
        return

    output = dict(
        s=struct.unpack('8s', code[:8])[0],
        n=struct.unpack('>H', code[8:10])[0],
        k=struct.unpack('>H', code[10:12])[0],
        q=struct.unpack('<d', code[12:])[0]
    )
    return output


# %%
'''
Data encoding and decoding
'''


def generate_package(n=0):
    '''
    Generate the package of the given time (n)

    Args:
        param: n: The idx number of the package;

    Return:
        return: n: the input n;
        return: k: The length of the bytes;
        return: q: The time stamp of the package;
        return: code: The code of the package in bytes;
        return: data: The raw data in numpy array.
    '''
    data = np.random.randint(-1000, 1000, (data_length, channels))
    array = data.reshape(np.prod(data.shape)).tolist()
    code = b''.join([struct.pack('<i', e) for e in array])
    k = len(code)
    q = time.time()
    return n, k, q, code, data


def decode_body(code):
    '''
    Decode the data from the body bytes

    Args:
        param: code: The decoding code;

    Return:
        return: data: The decoded data in numpy array.
    '''
    array_length = data_length * channels
    array = struct.unpack(f'<{array_length}i', code)
    data = np.asarray(array).reshape(data_length, channels)
    return data


# %%
if __name__ == '__main__':
    n, k, q, code, data = generate_package()
    print('The code info is', n, k, q)

    print('---- Header Check ----')
    header = encode_header(n, k, q)
    print(len(header), header)

    output = decode_header(header)
    print(output)

    print('---- Decode Check ----')
    data2 = decode_body(code)
    print('The difference values are', np.unique(data - data2))

# %%
