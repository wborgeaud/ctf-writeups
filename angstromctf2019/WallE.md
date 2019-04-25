# Wall-E - 130 points - 53 solves
## Useless RSA padding

Looking at the source code, we see an obvious bug in the line
```python
m = bytes_to_long(flag.center(255,'\x00'))
```
since this pads the flag **only** to the right. Let `p` be the number of padding bits to the right of the flag. Then the padding just multiplies the flag by `2**p`. Therefore, `c = 2**(e*p)*flag**e mod n` and thus 
```
flag**e = 2**-(e*p)*c mod n
```
The byte-length of `flag` is at most 86 and the bit-length of `n` is 2048. 
If the length of `flag` is 85 or less, the bit-length of `flag**3` is at most `3*8*85=2040<2048` and so the encryption doesn't loop around `n`. In that case we simply take the integer cube-root of `2**-(e*p)*c` and get the flag.

If the length of `flag` is 86, the bit-length of `flag**3` is at most `3*8*86=2064`. Thus, 
```
flag**3 =  2**-(e*p)*c + k*n
``` 
for `k<2**16`. We simply loop over these values of `k` and take the cube-root until we find a valid flag.

Here is the python code:
```python
from Crypto.Util.number import inverse, bytes_to_long, long_to_bytes
from binascii import *
from sympy import integer_nthroot
n = 16930533490098193592341875268338741038205464836112117606904075086009220456281348541825239348922340771982668304609839919714900815429989903238980995651506801223966153299092163805895061846586943843402382398048697158458017696120659704031304155071717980681280735059759239823752407134078600922884956042774012460082427687595370305553669279649079979451317522908818275946004224509637278839696644435502488800296253302309479834551923862247827826150368412526870932677430329200284984145938907415715817446807045958350179492654072137889859861558737138356897740471740801040559205563042789209526133114839452676031855075611266153108409
e = 3
c = 11517346521350511968078082236628354270939363562359338628104189053516869171468429130280219507678669249746227256625771360798579618712012428887882896227522052222656646536694635021145269394726332158046739239080891813226092060005024523599517854343024406506186025829868533799026231811239816891319566880015622494533461653189752596749235331065273556793035000698955959016688177480102004337980417906733597189524580640648702223430440368954613314994218791688337730722144627325417358973332458080507250983131615055175113690064940592354460257487958530863702022217749857014952140922260404696268641696045086730674980684704510707326989
seen = []
for l in range(87):
    print(l)
    lp = (255-l)//2
    if lp in seen:
        continue
    else:
        seen.append(lp)

    A = 2**(8*lp*e)
    Ainv = inverse(A,n)
    cu = (c*Ainv)%n
    bam = 24*l - 2048 + 1
    bam = bam+1 if bam>0 else 1
    for j in range(2**bam):
        m = integer_nthroot(cu+j*n,3)[0]
        m = long_to_bytes(m)
        if b'actf' in m:
            print(m)
            break
```

which outputs the flag `actf{bad_padding_makes_u_very_sadding_even_if_u_add_words_just_for_the_sake_of_adding}`.
