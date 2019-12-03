#import md5
import hashlib
#from tqdm import tqdm
#from pwnlib.util.fiddling import unhex, enhex
import string
import itertools

from pwn import *

while True:

	port = remote("167.71.62.250",12439)
	context.update(arch='amd64', log_level='debug')

	l = port.recvline()

	chal = l[-7:].strip()
	print("goal is ",chal)

	hash_type = l[-21:-18]
	print(hash_type)

	#chal = "5e8ccf"
	if hash_type == "md5":
		md5 = True
		break
	elif hash_type == "256":
		md5 = False
		break
	else:
		port.close()

#chal = "09304b"

for char_list in itertools.permutations(string.ascii_lowercase):
    s = "".join(char_list)

    if md5:
    	m = hashlib.md5()
    else:
    	m = hashlib.sha256()

    m.update(s.encode('ascii'))
    h = m.hexdigest()
    # print(h[-6:])
    if h[-6:] == chal:
        print("\nFound it!")
        print(s)
        break

port.send(s+"\n")
port.interactive()