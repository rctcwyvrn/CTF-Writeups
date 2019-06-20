from pwn import *

context.update(arch='amd64', log_level='debug')
s = remote('tania.quals2019.oooverflow.io', 5000)
s.interactive()