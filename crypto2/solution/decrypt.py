from Crypto.Util.number import inverse, long_to_bytes
from scapy.all import PcapReader

packets = PcapReader('crypto2.pcap').read_all()
p = (packet.payload.payload.payload for packet in packets)
tcp_packets = b''.join(filter(bool, map(bytes, p))).split(b'\n')
data = [ int(i.decode(), 16) for i in tcp_packets if i ]

# from server: A, g, p
A, g, p = data[:3]
# from client: B, nonce (encrypted)
B, nonce = data[3:5]
# from server: nonce**2 (encrypted)
n2 = data[5]

# vulerable in handshake part

# nonce_enc = nonce * s % p
# n2_enc = nonce * nonce * s % p
# n2_enc * nonce_enc**-1 -> nonce (raw)
raw_nonce = n2 * inverse(nonce, p) % p
s = nonce * inverse(raw_nonce, p) % p
s_inv = inverse(s, p) # decryption key

x = b''
for i in data[7:]:
    dec = s_inv * i % p
    r = long_to_bytes(dec)
    x += r[1:]

print(x.decode('ascii'))
