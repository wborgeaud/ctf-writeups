# HackTheBox write-ups

Write-ups for active boxes are encrypted using AES-CBC with the `root.txt` hash of the box as the password.

Example decryption:
```bash
openssl enc -d -aes-256-cbc -in Craft.md.enc -out Craft.md -k <root.txt hash>
```
