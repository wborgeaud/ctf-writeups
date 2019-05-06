# Crunchy - 50 points - 73 solves
# Binary recurrence sequence modulo prime

We get a recurrence relation `x(n) = 6*x(n-1)+x(n-2)`, with `x(0)=0,x(1)=1`. The flag is `INSA{x(g)%p}` for a very large value of `g` and a prime `p`.

This challenge is trivial to solve using a module of sage I discovered: `sage.combinat.BinaryReccurenceSequence`. With this module we can easily find the period of `x` modulo `p`. Then we just need to reduce `g` modulo this period and we get the flag. Here is the solution script:
```python
p = 100000007
T = BinaryRecurrenceSequence(6,1)
period = T.period(p)
g = 17665922529512695488143524113273224470194093921285273353477875204196603230641896039854934719468650093602325707751568
trunc_g = g%period
print T(trunc_g)%p
```
which gives the flag `INSA{41322239}`.
