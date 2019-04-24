# Runes
## Paillier cryptosytem

We are given numbers `n, g, c` and the hint *Paillier*. Googling for it, we discover the Paillier cryptosystem, which is based on the hardness of [decisional composite residuosity assumption](https://en.wikipedia.org/wiki/Decisional_composite_residuosity_assumption), which is weaker than integer factorization. This is good news since the parameter `n` is easily factored.

It is then a matter of copy-pasting the algorithm on Wikipedia to get the flag:
```python
from math import gcd
from Crypto.Util.number import inverse
from binascii import unhexlify
n= 99157116611790833573985267443453374677300242114595736901854871276546481648883
g= 99157116611790833573985267443453374677300242114595736901854871276546481648884
c= 2433283484328067719826123652791700922735828879195114568755579061061723786565164234075183183699826399799223318790711772573290060335232568738641793425546869

p = 310013024566643256138761337388255591613
q = 319848228152346890121384041219876391791
assert n == p*q

def L(x):
    return (x-1)//n

lamb = (p-1)*(q-1)//gcd(p-1,q-1)
mu = inverse(L(pow(g,lamb,n**2)),n)
m = L(pow(c,lamb,n**2))*mu%n
print(unhexlify(hex(m)[2:]))
```
which ouptuts the flag `actf{crypto_lives}`.
