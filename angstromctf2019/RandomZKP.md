# Random ZKP
## Lattice-based ZKP (with randomness). 

This time we get to play with the actual protocol. We need to find a n-vector `s` to get the flag. We get a nxn-matrix `A` and a n-vector `b` such that `A*s+e=b`, with `e` following a normal distribition around 0.

The server gives random n-vectors `r` or `r+s` along with `A*r+e` with `e` having the same distribution as above. We cannot get both `r` and `r+s` (otherwise the challenge would again be trivial). 

The way I solved it (there are maybe other ways) is to realize that given `r+s` and `A*r+e`, we can compute 
```
A*(r+s)-A*r-e=A*s-e
```
for many random values of `r` and `e` by asking the server K times.

Averaging the results, we get `A*s-sum(e_i)/K`. By the law of large numbers, `sum(e_i)/K` converges to 0 as K grows to infinity. 

I ran this with K=300, then rounded the average to get `c` and assumed it was equal to `A*s`. If it's not the case, you can increase K:
```python
def get_A_s():
    r = remote('54.159.113.26', 19004)
    x = r.recvuntil('Choice: ')
    d = DerSequence()
    s = unhexlify(x.split(b': ')[1].split(b'\n')[0])
    y = d.decode(s)
    A_r = np.array(y)

    r.sendline('1')
    x = r.recvuntil('\n')[:-1]
    d = DerSequence()
    r_s = unhexlify(x.split(b'r+s: ')[1])
    z = d.decode(r_s)
    r_s = np.array(z)

    r.close()
    return np.mod(lwe.mul(A,r_s)-A_r,q)

c_mat = []
for i in range(300):
    print(i)
    rs = get(1)
    c_mat.append(rs)

c_mat = np.array(c_mat)
c = c_mat.mean(0)
```

Then, I used sage to compute the solution `s` of the system of equations `A*s=c mod q`:
```
sage: q = 2**15
sage: A = matrix(Integers(q),A)
sage: c = matrix(Integers(c),c).transpose()
sage: s = A.solve_right(c)
```

I then decrypted the flag as in the challenge RandomZKP to get the flag `actf{oops_sorry_for_the_lack_of_randomness}`.
