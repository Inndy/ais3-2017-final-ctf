import base64
from Crypto.Util import number

def RSA(n, e):
    global N, E
    N, E = n, e

lines = open('encrypted').readlines()
print(lines[1])
print(lines[2])
eval(lines[0])
data = base64.b64decode(lines[3].strip())

def xor(a, b):
    return bytes(i ^ j for i, j in zip(a, b))

print('[+] Generating reverse hash table...')
dec = {}
for i in range(0x10000):
    x = b'%.4x' % i
    if i & 0xff == 0:
        print('Progress: %5.1f%%' % (i * 100 / 0x10000), end='\r', flush=True)
    v = number.bytes_to_long(x)
    dec[pow(v, E, N)] = x

print('[+] Decrypting RSA encryption...')
raw = b''
for i in range(256, len(data), 256):
    prev = data[i-256:i]
    curr = int(xor(prev, data[i:i+256]).hex(), 16)
    raw += dec[curr]

print('[+] layer4 decrypted: %r' % raw)
data = bytes.fromhex(raw.decode())
r = number.inverse(17, 251)

def layer3(data, key):
    output = []
    for i in data:
        key = (key * 0xc8763 + 9487) & 0xff
        output.append(i ^ key)
    return bytes(output)

print('[+] Decrypting layer3 stream cipher...')
for k in range(256):
    decrypted = bytes(i * r % 251 for i in layer3(data, k))

    if decrypted[3:5] == b'3{' and decrypted[-2:] == b'}\n':
        print('[+] Decrypted: %r' % decrypted)
        print('[*] You can use http://quipqiup.com/ to solve substitution cipher')
        break
