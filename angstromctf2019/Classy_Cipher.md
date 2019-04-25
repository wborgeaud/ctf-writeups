# Classy Cipher - 20 points - 708 solves
## Classic caesar cipher:

```python
c = ':<M?TLH8<A:KFBG@V'
for s in range(0xff):
    p = ''.join((chr((ord(c[i])+s)%0xff)) for i in range(len(c)))
    if 'actf' in p:
        print(p)
```

which returns the flag `actf{so_charming}`.
