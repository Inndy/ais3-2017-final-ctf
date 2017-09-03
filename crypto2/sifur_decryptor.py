from Crypto.Util import number

def sifur_dec(self, x):
    if self.S is None:
        self.S = number.inverse(self.s, self.p)
    return (x * self.S) % self.p
