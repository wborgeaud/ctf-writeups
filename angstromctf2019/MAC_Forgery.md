# MAC Forgery

CBC-MAC forgery with chosen IV. We get a `welcome` message along with its CBC-MAC (including the IV). The goal is the find **any** other message on which we can compute a valid CBC-MAC (with control on the IV).

The CBC-MAC implementation somewhat prevents from tampering by prepending the block length to the message. The block length of `welcome` is 7, therefore the CBC-MAC is computed with 
```
  IV
------
000007
------
  M1
------
...
------
  M7   ---> MAC
```
We can derive a new message from `welcome` by appending to it a modified copy of itself.

Here the new message:
```
  IV'
------
00000f ---> Same as E(IV^0007)
------
  M1
------
...
------
  M7   ---> Same MAC as before
------
 LOAD  ---> Same as E(IV^00007)
------
  M1
------
...
------
  M7   ---> Same MAC as before
```

We need to take care of the following details:
* The new message block length is 15, thus we change the initial `IV` to `IV'` so that `IV' ^ 0000f = 00007`.
* The string `LOAD` is designed so that `E(LOAD^MAC) = E(00007^IV)`. That way, the chain of encryptions is reproduced for the copy of `welcome`. We just set `LOAD = MAC ^ 00007 ^ IV`.

Here is the (sloppy) python implementation:
```python
from pwn import *
from binascii import hexlify, unhexlify
from Cryptodome.Util.Padding import pad
from Cryptodome.Util.number import long_to_bytes
from Cryptodome.Util.strxor import strxor
from Cryptodome.Random import get_random_bytes
from time import sleep

split = lambda s, n: [s[i:i+n] for i in range(0, len(s), n)]

welcome_or = b'''\
If you provide a message (besides this one) with
a valid message authentication code, I will give
you the flag.'''

welcome = pad(welcome_or,16)
welcome = split(welcome,16)
welcome.insert(0, long_to_bytes(len(welcome), 16))

r = remote('54.159.113.26', 19002)

x = r.recvuntil('Message: ')
mac = x.split(b'MAC: ')[1].split(b'\n')[0]
mac = unhexlify(mac)
iv = mac[:16]
mac = mac[16:]
payload = strxor(strxor(welcome[0],mac),iv)

niv = strxor(strxor(iv,long_to_bytes(len(welcome)-1,16)),long_to_bytes(2*len(welcome)-1, 16))

fin = welcome[1:] + [payload]
fin = b''.join(fin) + welcome_or

r.sendline(hexlify(fin))
r.sendline(hexlify(niv)+hexlify(mac))
sleep(2)
ans = r.recv()
print(ans)
r.close()
```
which outputs the flag `actf{initialization_vectors_were_probably_a_bad_idea}`.
