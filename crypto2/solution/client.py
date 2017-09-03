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

S.writeline('echo This is too easy for you, enjoy next stage!')
get_response()
S.writeline('detail')
get_response()
S.writeline('get-flag')
print(S.readline()[:-1])
print(S.readline()[:-1])
print(S.readline()[:-1])
for i in range(200, 205):
    S.writeline(str(i))
    print(S.readline()[:-1])
S.writeline('xx')
get_response()
S.writeline('exit')
