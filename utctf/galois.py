import itertools
import galois_server
import numpy as np
import random
import subprocess
from Crypto.Util.number import long_to_bytes, bytes_to_long

# oh my look at all those repeated nonces

# from pwn import *
# s = remote("crypto.utctf.live", 9004)
# def send_enc_req(msg):
# 	s.recvuntil("Select option: ")
# 	s.send("1\n")
# 	s.recvuntil("Input a string to encrypt (must be at least 32 characters):")
# 	s.send(msg+ "\n")
# 	s.recvuntil("Here is your encrypted string & tag, have a nice day :)")
# 	s.recvline()
# 	e = s.recvline()
# 	parts = e.split(",")
# 	print("ciphertext = '" +  parts[0][2:-1] +  "' | tag = '" + parts[1][2:-4]) + "'"
# 	x = bytearray.fromhex(parts[0][2:-1].strip())

# 	tag = parts[1][2:-4]
# 	if not len(tag) % 2 == 0:
# 		y = bytearray.fromhex("0" + tag)
# 	else:
# 		y = bytearray.fromhex(tag)
# 	return x,y

# subtracts/adds two hex over the field (which i pray will be the same :P, but I somehow doubt), but I dont know what -1 is in the field so can't multiply :c
def gf_sub(x1,x2):
	assert(len(x1)==32)
	#return int.from_bytes(x1, byteorder='big', signed='false') ^ int.from_bytes(x2, byteorder='big', signed='false')
	return int(x1,16) ^ int(x2,16)

def blockify(xs, block_size = 16):
	res = []
	for i in range(len(xs)//block_size):
		res.append(xs[block_size * i : block_size * (i+1)])
	if(len(xs) % block_size != 0):
		res.append(xs[block_size * (i+1):])
	return res

def send_enc_req(msg):
	return debug_send(msg)

def debug_send(msg):
	msg = msg.encode()

	blocks = blockify(msg)
	last_block = blocks[-1]
	print("encrypting: ",blocks)

	c,t =  galois_server.aes_gcm_encrypt(msg)
	L = 0 + 8*len(last_block)
	print("got c=", blockify(c,32), " | tag = ",t, " | L = ", L) #32 because we're blockifying hex now

	c += "0" * (32-(2*len(last_block)))
	print("padded c = ", blockify(c, 32))
	return c, t, L

same_nonce = []
for i in range(10):
	#same_nonce.append(send_enc_req(str(i)*16 + str(i)*random.randint(0,4))) #forces us up to 3 ciphertext blocks >:C
	same_nonce.append(send_enc_req(str(i)*16))

factors = {}

for [(C1,T1,L1),(C2,T2,L2)] in itertools.combinations(same_nonce,2):
	#print("Sending ", [(C1,T1,L1),(C2,T2,L2)])
	x = subprocess.check_output(["./nonce-disrespect/tool/recover", "", str(C1), str(T1), "", str(C2), str(T2)])
	#print("got", x)
	factor = int(x[:-1].decode(),16)

	if factor in factors:
		factors[factor] +=1
	else:
		factors[factor] = 1

	# g = []
	# #print("total", C1,C2)
	# for c1,c2 in zip(blockify(C1,32),blockify(C2,32)):
	# 	#print("pairs", c1,c2)
	# 	g.append(gf_sub(c1,c2))
	# g.append(L1 ^ L2)
	# g.append(gf_sub(T1,T2))

	# print("polynomial = ", g)
	# roots = np.roots(g)
	# print("roots = ", roots)

	# for root in roots:
	# 	if root.imag == 0.0:
	# 		if root in factors:
	# 			factors[root]+=1
	# 		else:
	# 			factors[root]=1

print("key candidates:", factors, len(factors))

best = ""
best_val = 0
for root, value in factors.items():
	if value > best_val:
		best = root.real
		best_val = value

h = int(best)
print("best = ", h, "best_val = ", best_val)
print("actual = ", galois_server.H)
print("flag =", galois_server.flag_enc)


# import ghasher
# hasher = ghasher.GHASH(bytearray.fromhex(galois_server.flag_enc[0]), ghasher._get_ghash_clmul())

# import ghasher
# ghash = ghasher.GHASH(long_to_bytes(best), b"", bytearray.fromhex(hash_me)).hex()
# print("got ghash = ", ghash)

# import aes_gcm as gcm
# sender = gcm.AES_GCM(best)
# ghash = sender.ghash(b"", bytearray.fromhex(hash_me))
#ghash = long_to_bytes(ghash).hex()

#print("got ghash = ", ghash)

print("cmd = ", ["./nonce-disrespect/tool/recover", 
	"", 
	str(same_nonce[0][0]), 
	str(same_nonce[0][1]), 
	"", 
	galois_server.flag_enc[0], 
	long_to_bytes(best).hex()])

for (C1,T1,L1) in same_nonce:
	tag = subprocess.check_output(["./nonce-disrespect/tool/recover", 
		b"", 
		str(C1), 
		str(T1), 
		b"", 
		galois_server.flag_enc[0], 
		long_to_bytes(best).hex()])

# C1 = int(same_nonce[0][0],16) % 128
# C2 = int(galois_server.flag_enc[0],16) % 128

# T1 = int(same_nonce[0][1],16) % 128

# L1 = same_nonce[0][2] % 128
# blocks = blockify(bytearray.fromhex(galois_server.flag_enc[0]))
# last_block = blocks[-1]
# L2 = (0 + 8*len(last_block)) % 128

# print(C1,C2,T1,L1,L2)

# from pyfinite import ffield
# F = ffield.FField(128)
# tag = F.Add(F.Add(F.Multiply(F.Multiply(h,h), F.Add(C1,C2)), F.Multiply(h, F.Add(L1,L2))), T1)

from pynitefields import * 
gf = GaloisField(128)
A = gf[C1] + gf[C2]
B = gf[L1] + gf[L2]
print(A,B, gf[h % 128])
tag = A * gf[h % 128] * gf[h % 128] + B * gf[h % 128] - gf[T1]

print("got tag =", tag)
print("actual tag = ", galois_server.flag_enc[1])
print("test decryption = ", galois_server.aes_gcm_decrypt(bytearray.fromhex(galois_server.flag_enc[0]), bytearray.fromhex(galois_server.flag_enc[1])))
print("retrieved flag  = ", galois_server.aes_gcm_decrypt(bytearray.fromhex(galois_server.flag_enc[0]), tag[:-1]))