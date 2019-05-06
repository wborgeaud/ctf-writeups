# Dashlame Part 2 - 126 points - 35 solves
## Meet-in-the-middle attack with partial information

Interesting challenge showing that double encryption really isn't better than simple encryption, mainly because of the meet-in-the-middle attack.

We get a python script implementing a password manager. The password manager takes a database of passwords and encrypts it twice using AES-CBC. Each AES encrytption is done with a key and iv derived from a passphrase belonging to a given list of around 500'000 words. We are given an encrypted database `admin.dla` and need to decrypt it to get the flag.

Let `P` be the database plaintext, `E1` the first encryption and `E2` the second encryption. 

The length of `E1` is divisible by the AES blocksize which is 16. Therefore, the padding scheme of the script adds 15 random character + the character `\xa0` at the end of `E1` before encryption. This is our fist attack vector. We decrypt `E2` with each of the ~500'000 passphrase and keep only the ~2'000 passphrase resulting in a decryption ending with `\xa0`. 

By playing with the code, we know that the database plaintext begins with the string *SQLite*. This is our second attack vector. For each of the ~2'000 possible decryptions ending with the character `\xa0`, we decrypt the first block using all of the ~500'000 passphrases. If one of them begins with *SQLite*, we hit the jackpot. 

The whole process runs in around 10 seconds on my laptop and gives the passphrases *spanish* and *inquisition*. Decrypting the `admin.dla` database with them gives the flag `INSA{D0_you_f1nD_it_Risible_wh3N_I_s4y_th3_name}`.
