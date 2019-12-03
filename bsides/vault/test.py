from pwn import *


context.update(arch='amd64', log_level='debug')
p = process(["./thevault.nix"])
p.recvuntil("Enter password:")
p.send("A"*100 + "\n")
#p.interactive()