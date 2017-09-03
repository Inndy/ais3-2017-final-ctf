import base64
import hashlib
import socket
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from easysock import *
from sifur import *

s = socket.create_connection(('0', 5566))
ns = NumberSocket(s)

# recv ElGamal public key
A, g, p = [ ns.read() for _ in range(3) ]

# generate private key
y = number.getPrime(512)

# create cipher instance
c = Sifur(p, g, y)
# performance key exchange
c.second(A)
# nonce used in handshake
nonce = number.getPrime(512)

print('A = 0x%x' % A)
print('B = 0x%x' % c.A)
print('g = 0x%x' % g)
print('p = 0x%x' % p)
print('s = 0x%x' % c.s)
print('n = 0x%x' % nonce)


# send public key from client
ns.write(c.A)
# handshake
ns.write(c.encrypt(nonce))

# check response from nonce
k = c.decrypt(ns.read(), as_int=True)
print('response = %x' % k)
assert (nonce * nonce) % p == k

# protocol handshake is ready
S = EasySocket(SifurSocket(ns, c))
chall = base64.b64decode(S.readline())
print('chall = %r' % chall)
i = 0
while True:
    if hashlib.sha1(b'%s%d' % (chall, i)).hexdigest()[:5] == '12345':
        break
    i += 1

print('i = %d' % i)
S.writeline(str(i))

S.readline()
S.writeline('root')
S.readline()
S.writeline('c80aef4a14d00c6dc23ff3d30d32641b')
assert 'welcome' in S.readline()

def get_response():
    while True:
        k = S.readline()[:-1]
        if k.startswith('=== end of command ==='):
            break
        print(k)


S.writeline('get-flag')
n, e, C = [ int(S.readline().split()[-1], 16) for _ in range(3) ]

def oracle(i):
    S.writeline(str(i))
    return 1 if 'odd' == S.readline()[:-1] else 0

# lsb oracle attack
skip_rounds = 512
UP = n >> skip_rounds
LOW = 0

cur_C = C * pow(2**skip_rounds, e, n) % n
for i in range(1024 - skip_rounds):
    print('Oracle round %d\n --> %r\n --> %r' % (
            i,
            number.long_to_bytes(UP),
            number.long_to_bytes(LOW)
        )
    )
    cur_C = (cur_C * pow(2, e, n)) % n
    if oracle(cur_C) == 0:
        UP = (UP + LOW) >> 1
    else:
        LOW = (UP + LOW) >> 1

pt = number.long_to_bytes(UP).decode('latin1')
qt = number.long_to_bytes(LOW).decode('latin1')
print('UP:  %x' % UP)
print('LOW: %x' % LOW)
print(pt)
print(qt)

for x in range(0x20, 0x7f):
    for y in range(0x20, 0x7f):
        corr_pt = pt[:-2] + chr(x) + chr(y)
        if pow(number.bytes_to_long(corr_pt.encode()), e, n) == C:
            print(corr_pt)
            exit()
