# Postman - HackTheBox
## Linux - Easy

### User
After the `nmap`, we find that ports 22, 80, 6379, and 10000 are open, with `Redis` and `Webmin` running on the last two ports. Following [this](http://reverse-tcp.xyz/pentest/database/2017/02/09/Redis-Hacking-Tips.html) we put our public SSH key in `/var/lib/redis/.ssh/authorized_keys`. We can then SSH to `redis@postman.htb`.

`LinEnum.sh` finds an RSA key in `/opt/id_rsa.bak`. We can crack the passphrase with `ssh2john` and `rockyou.txt` and we get `computer2008`. We can `su Matt` with this password and get `user.txt`.

### Root
We use the (exploit/linux/http/webmin_packageup_rce)[https://github.com/rapid7/metasploit-framework/blob/master/documentation/modules/exploit/linux/http/webmin_packageup_rce.md) Metasploit module for `Webmin` with creds `Matt:computer2008` and we get a root shell!
