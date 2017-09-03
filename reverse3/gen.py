#!/usr/bin/env python3
import io
import os
import random
import subprocess
import sys

flag = 'ais3{r3v3rs1ng_vm_p4ck3r_jus7_l1k3_1nc3pt10n}'

buff = ''

def emit(x):
    global buff
    buff += x + '\n'

def p(x):
    for i in x:
        emit('movi r1, 0x%.2x ; %r' % (ord(i), i))
        emit('movi ra, 1 ; write')
        emit('sys')

emit('.sect text')
emit('call $anti_sidechannel')
p('Input flag: ')
emit('movi r5, 0')

for i in flag:
    k = ord(i)

    a = random.randint(1, 0xff)
    b = random.randint(1, 7)
    c = random.randint(1, 0xffff)

    k = (k * a) & 0xffff
    k = (k << b) & 0xffff
    k = (k ^ c) & 0xffff

    emit('call $anti_sidechannel')
    emit('movi ra, 0 ; read')
    emit('sys')
    emit('muli r1, ra, 0x%.2x ; k * a' % a)
    emit('shri r2, r1, 0x%.2x ; k << b' % (0xffff & -b))
    emit('xori r3, r2, 0x%.4x ; k ^ c' % c)
    emit('addi r4, r3, 0x%.4x ; cmp' % (0xffff & -k))
    emit('jni  r5, r4, $badflag')

p('Good flag for you!\n')
emit('hlt')
emit('badflag:')
p('Not the flag\n')
emit('hlt')

emit('anti_sidechannel:')
emit('.include zstdlib/anti-sidechannel.zasm')
emit('ret')

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), 'lib/python'
))

from zzvm import *

p = Parser(io.StringIO(buff))
p.build()
shellcode = p.section_bodies['TEXT']

def encrypt(shellcode):
    print('Length of shellcode: 0x%x' % len(shellcode))
    m = bytearray(shellcode)
    k = (0x55, 0x22)
    for i in range(2, len(shellcode)):
        m[i] ^= shellcode[i - 2] ^ 0xff ^ k[i & 1]
        if i & 1 == 0:
            q = (i - 2)
            m[i] ^= q & 0xff
            m[i+1] ^= (q >> 8) & 0xff
    return m

with open('encrypted.zasm', 'w') as fout:
    fout.write('.db ')
    fout.write(', '.join('0x%.2x' % i for i in encrypt(shellcode)))

os.system('./utils/zzassembler game.zasm game.zz')
