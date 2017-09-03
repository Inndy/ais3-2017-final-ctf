import textwrap

__all__ = [
    'zz_encode_byte',
    'zz_encode_data',
    'zz_decode_data'
]

def zz_encode_byte(b):
    return bin(b)[2:].zfill(8).translate(str.maketrans('10', 'Oo')).encode()

def zz_encode_data(data):
    return b''.join(zz_encode_byte(i) for i in data)

def zz_decode_data(data):
    bindata = data.decode('ascii').translate(str.maketrans('Oo', '10'))
    return bytes(int(i, 2) for i in textwrap.wrap(bindata, 8))
