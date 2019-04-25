# Powerball - 200 points - 51 solves

We need to find 6 numbers `b1,...,b6` between 0 and 4096. We are given random numbers `x1,...,x6` and `m1,...,m6` with
```
mi = bi + (v-xi)**d mod n
```
for a secret `d` and a given v. However, we know `n` and `e` with `e*d=1 mod phi(n)`.

Therefore, for each `i`, we just have to loop over all possible values of `bi` to check if 
```
(mi-bi)**e = v-xi mod n
```
which is fast since `0<=bi<4096`. We then outputs the found `bi`s to get the flag.

Here is the python implementation:
```python
from pwn import *
import re

e = 65537
n = 24714368843752022974341211877467549639498231894964810269117413322029642752633577038705218673687716926448339400096802361297693998979745765931534103202467338384642921856548086360244485671986927177008440715178336399465697444026353230451518999567214983427406178161356304710292306078130635844316053709563154657103495905205276956218906137150310994293077448766114520034675696741058748420135888856866161554417709555214430301224863490074059065870222171272131856991865315097313467644895025929047477332550027963804064961056274499899920572740781443106554154096194288807134535706752546520058150115125502989328782055006169368495301

r = remote('54.159.113.26', 19001)
x = r.recvuntil('v: ')
x = eval(re.findall(b'\[.*\]',x)[0])
r.sendline('0')
bla = r.recvuntil('Ball 1: ')
m = eval(re.findall(b'\[.*\]',bla)[0])
for i in range(6):
    for b in range(4096):
        if pow(m[i]-b,e,n) == (-x[i])%n:
            r.sendline(str(b))
            bla = r.recv()
            break

bla = r.recv()
print(bla)
```
which outputs the flag `actf{no_more_free_oblivious_transfers}`.

