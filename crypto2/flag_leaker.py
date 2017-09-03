from Crypto.Util.number import *
from flag import flag, n, e, d

eflag = pow(bytes_to_long(flag.encode()), e, n)

def run(s):
    s.writeline('n = 0x%x' % n)
    s.writeline('e = 0x%x' % e)
    s.writeline('encrypted flag = 0x%x' % eflag)

    while True:
        try:
            i = int(s.readline())
            if i < 10 or i > n:
                s.writeline('bad')
                break

            v = pow(i, d, n)
            if v & 1:
                msg = 'odd'
            else:
                msg = 'even'

            s.writeline(msg)
        except:
            s.writeline('bad')
            break
