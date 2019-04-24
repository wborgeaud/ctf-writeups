# Half

The flag `f` is split in two halves `f[:mid]` and `f[mid:]`. We get the value `f[:mid] ^ f[mid:] := c = \x15\x02\x07\x12\x1e\x100\x01\t\n\x01"`.

Assuming that `f` is in standard format and starts with *actf{...}*, we get by xoring with `c` that `f[mid:]` starts with *taste* and `f[mid-1]=_`. So the flag is `f=actf{......_taste......}`.

By pure guessing (using the challenge description), we try the word *coffee* before *taste*. By xoring again with `c`, this gives `f = actf{coffee_tastes_good}` which looks like a plausible flag. And it turns out that it is correct.
