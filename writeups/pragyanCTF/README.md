CTF: Pragyan2019
===
## Info
* Category: Binary
* Challenge: Secret Keeper
* Solved by: Robert Xiao
* Writeup by: Howard Lin

## Solution
After decompiling the program with Ghidra we see that we need to log into the secret keeper with the username "admin", but the system prevents us from creating an account called that.

One solution is to abuse the way the program deletes accounts to create an admin account by inputting "admin" as a password. We see that the program only deletes the "user" part of the account, so we can write in whatever we want into the "username" slot of an account.

Steps:
1.) create 2 accounts with any passwords

Heap:
---
* user1
* pass1
* secret1
* user2
* pass2
* secret2
---

2.) delete both accounts

Heap:
---
* (free)
* pass1
* secret1
* (free)
* pass2
* secret2
---

3.) create a new account with password admin

Heap:
---
* (whatever you chose the new username to be)		<--malloc #1: the username
* pass1
* secret1
* ("admin")										                  <--malloc #2: the password
* pass2
* secret2
---

and then the secret is somewhere else and we don't really care

4.) now log in with admin and pass2 and you get the flag!


Example inputs:
1
aaa
bbb
1
ccc
xxx
2
aaa
bbb
3
2
ccc
xxx
3
1
eee
admin
2
admin
xxx

Thanks for reading!
