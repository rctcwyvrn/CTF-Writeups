from pwn import *


context.update(arch='amd64', log_level='debug')
r = remote("crypto.chal.csaw.io", 1001)

r.recvuntil("=")
print(r.recvline())

def send_to_enc(y):
	r.send("4\n")
	r.recvline()
	# r.send('fake_flag{%s}' % (('%X' % y).rjust(32, '0'))+"\n")
	# #r.recvuntil("=")
	# r.recvline()
	# r.recvline()
	# r.recvline()



for i in range(5):
	send_to_enc(i)


r.interactive()