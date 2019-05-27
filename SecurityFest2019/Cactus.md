# Cactus
## Weird approximate gcd problem 

Note: I didn't solve this challenge during the ctf. Since there aren't any write-ups available at the time of writing, I decided to write one.
We get a script `cactus.py`:
```python
import random
from math import log

class Oracle:

    def __init__(self, secret, bits=512):
        self.secret = secret
        self.bits = bits
        self.range = 2*self.bits

    def sample(self, w):
        r = random.randint(0, 2^self.range)
        idx = range(self.bits)
        random.shuffle(idx)
        e = sum(1<<i for i in idx[:w])
        return self.secret*r+e


o = Oracle(10)
for i in range(100):
    print o.sample(10)
```
and a file `output.txt` (that you can find in this directory) containing 100 large numbers, supposedly generated using `cactus.py`. Note that the line `o = Oracle(10)` should really be `o = Oracle(FLAG)`, and our goal is to find this flag. 

The first thing that jumps to mind is in the line `r = random.randint(0, 2^self.range)`, `2^self.range` looks like a typo for the exponentation which would be `2**self.range` in python. With the default value `self.range=1024`, `2^self.range` is 1026 which is brute-forceable. 

The error term `e` is made of a large number with 10 random bits set. Looking at the elements of `output.txt` in binary, I found that the 78th has its seven highest bits looking randomly set:
```
>>> bin(l[78])
0b100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000001000000000001000000000000000000000000100000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000001000100000011111010100110101000011100101101001101101111011101000110110010010010010101000000110101001101101010010111011100000000101001000100111101001111111100000001011000100110101101000010011101011100000010100010110010010001000111011101010000100110100010010010000001111011101010100000101110010001001010111011101100
```
So, supposedly, the 7 first set bits come from `e`. Thus, we only need to brute-force the last 3 bits coming from `e`!

Here is my first try:
```python
# a is l[78] starting from the 8th bit set.
a=int('1000100000011111010100110101000011100101101001101101111011101000110110010010010010101000000110101001101101010010111011100000000101001000100111101001111111100000001011000100110101101000010011101011100000010100010110010010001000111011101010000100110100010010010000001111011101010100000101110010001001010111011101100',2)
for i in range(313):
   for j in range(i):
     for k in range(j):
       x = a-2**i-2**j-2**k # x is a minus 3 random bits.
       for d in get_div(x): # get_div returns the divisors of x smaller than 1026.
         s=long_to_bytes(x//d) # we divide a by a divisor to get a potential flag.
         if b'ctf' in s: # we check if 'ctf' is a substring. 
           print('divisor: '+str(d))
           print(s)
```
Running this, we get outputs looking like this:
```
divisor: 604
b"sctf{wi\xe23\xd4z'\x81\xf8O\xaf\xb5\xed\xe1`\xc8O.\t\x16\x1bk\xc4\xdc\x1ba\x8b<'\xb10n}"
41
divisor: 604
b"sctf{wi\xe23\xd4z'\x81\xf8O\xaf\xb5\xed\xe1`\xc8O.\t\x16\x1bk\xc4\xdc\x1ba\x8b<'E\x96'E"
divisor: 604
b"sctf{wi\xe23\xd4z'\x81\xf8O\xaf\xb5\xed\xe1`\xc8O.\t\x16\x1bk\xc4\xdc\x1ba\x8b<'E\x96 }"
divisor: 604
b"sctf{wi\xe23\xd4z'\x81\xf8O\xaf\xb5\xed\xe1`\xc8O.\t\x16\x1bk\xc4\xdc\x1ba\x8b<'E\x94uE"
```
We see the beginning of a flag starting with `sctf`, always with the divisor 604. We guess that this is the real value of `r` and stop looking for other divisors, which speeds up the brute-force. Finally, we only print stings with only printable characters:
```python
from string import printable
for i in range(313):
  for j in range(i):
    for k in range(j):
      x = a-2**i-2**j-2**k
      s=long_to_bytes(x//604)
      if b'ctf' in s and all([chr(le) in printable for le in s]):
        print(s)
```
which outputs
```
b'sctf{wh00ps_th4t_w4sntzSxp0nent1ati0n}'
b'sctf{wh00ps_th4t_w4snt_3xp0nent1ati0n}'
```
I guess that the second one is probably the flag.

### Post-mortem:
During the ctf, I tried way more complex methods, researching the *approximate gcd problem* which is used in some crypto algorithm. In my head it was clear that I should use many number in the output and somehow find the flag by computing their approximate gcd.

As we can see in this write-up, we actually only need one of the output (albeit smartly chosen so that a lot of the highest bits come from the error `e`) and that the solution can be found using a simple brute-force search on `r` and `e`. 

All in all, the solution isn't that interesting, but it's a good lesson for me that I shouldn't immediatly over-complicate things and first try the direct approach to solve a problem.
