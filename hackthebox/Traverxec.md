# Traverxec - HackTheBox

## Linux - Easy

### User

`Nmap` shows port 22 and 80 open, with 80 served by the `nostromo` web server. A quick `searchsploit` shows that this version of `nostromo` is vulnerable to RCE. We use the `exploit/multi/http/nostromo_code_exec` Metasploit module and get a shell as `www-data`. 

We read the `nostromo` configuration file in `/var/nostromo/conf/nhttpd.conf`:

```yaml
# MAIN [MANDATORY]
servername		traverxec.htb
serverlisten		*
serveradmin		david@traverxec.htb
serverroot		/var/nostromo
servermimes		conf/mimes
docroot			/var/nostromo/htdocs
docindex		index.html

# LOGS [OPTIONAL]
logpid			logs/nhttpd.pid

# SETUID [RECOMMENDED]
user			www-data

# BASIC AUTHENTICATION [OPTIONAL]
htaccess		.htaccess
htpasswd		/var/nostromo/conf/.htpasswd

# ALIASES [OPTIONAL]
/icons			/var/nostromo/icons

# HOMEDIRS [OPTIONAL]
homedirs		/home
homedirs_public		public_www
```

The last two lines are interesting. The folder `/home/david` cannot be read as `www-data`, however, going to `/home/david/public_www/` we have read access. There we find `/home/david/public_www/protected-file-area/backup-ssh-identity-files.tgz`. Sending this file to our box and unzipping it, we find that it's a backup of `/home` where we find an encrypted SSH key for `david`. A quick `ssh2john` gives the passphrase `hunter`,  and we can SSH to the box as `david` and get the `user.txt` flag.



### Root

We find the file `/home/david/bin/server-stats.sh` which contains the line 

```bash
/usr/bin/sudo /usr/bin/journalctl -n5 -unostromo.service | /usr/bin/cat 
```

Running `/usr/bin/sudo /usr/bin/journalctl -n5 -unostromo.service` gets us in a `less`-like interface, where we can execute commands by typing `!whoami` for example. We use this to get a reverse shell as root, and that's the box!

