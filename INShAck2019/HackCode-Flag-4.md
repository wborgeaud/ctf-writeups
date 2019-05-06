# Hack Code Flag 4 - 100 points - 64 solves
# Set cover problem

We get a list of 10'000 network routes. A route is a list of strings. We need to find a set of 126 such strings such that each route contains a string belonging to that set. This can be translated as a classical set cover problem. The universe is the set `{1,...,10000}` and the collection of sets is `{i | route i contains string s}` for each string `s`.

Approximating the set cover problem with the greedy algorithm gives a score of 128, which is good enough to get 3 flags but not the fourth. We therefore need a better algorithm. Instead of implementing one, I searched for an existing one in Python and found this [one](https://github.com/guangtunbenzhu/SetCoverPy). It manages to find a solution with score 126. Here is the script:
```python
import numpy as np
from SetCoverPy import setcover

routes = open('routes.txt').read().split()
routes = [x.split(',') for x in routes]
F = set(range(10000))
nets = list(set([x for y in routes for x in y]))
subsets = {n:[] for n in nets}

for i in range(len(routes)):
    for x in routes[i]:
        subsets[x].append(i)

# Building the matrix for the set cover solver
a = np.zeros((len(routes),len(nets)))
for j in range(len(nets)):
    a[subsets[nets[j]],j]=1
a = np.where(a==1,True,False)
# Costs are all one for this instance
cost = np.ones(len(nets))

g = setcover.SetCover(a,cost,maxiters=5)

sol, time = g.SolveSCP()
print(sol.sum())
print(g.s)
```
which outputs the solution of size 126.
