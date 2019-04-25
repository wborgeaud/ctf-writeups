# Lattice ZKP - 150 points - 28 solves
## Lattice-based ZKP (without randomness). 

I get into details on the protocol in the writup of *RandomZKP*.

Here we need to find a vector `s` to get the flag. We are given a server that outputs a random vector `r` or `r+s` but not both. After, playing around a bit, we quickly realize that `r` doesn't change between queries and is thus constant. We therefore ask for `r` then for `r+s`, and get `s=(r+s)-r`. Decrypting the flag is then easy...

Here is the python implementation:
```python
from pwn import *
from Cryptodome.Util.asn1 import DerSequence
from Cryptodome.Util.strxor import strxor
from Cryptodome.Hash import SHAKE256
from binascii import unhexlify
import numpy as np

def get(i):
    r = remote('54.159.113.26', 19003)
    x = r.recvuntil('Choice: ')
    d = DerSequence()
    s = unhexlify(x.split(b': ')[1].split(b'\n')[0])
    y = d.decode(s)
    y = np.array(y)

    r.sendline(str(i))
    x = r.recvuntil('\n')[:-1]
    d = DerSequence()
    sss = b'r+s: ' if i else b'r: '
    s = unhexlify(x.split(sss)[1])
    z = d.decode(s)
    z = np.array(z)

    r.close()
    return z

rs = get(1)
r = get(0)
s = rs-r

flag = open('lattice_zkp/flag.enc','rb').read()
s = bytes(np.mod(s,256).tolist())
shake = SHAKE256.new()
shake.update(s)
pad = shake.read(len(flag))
print(strxor(pad,flag))
```
which outputs the flag `actf{deep_into_that_darkness_learning_with_errors_goes}`.


