from pwn import *
import struct, os, sys
import subprocess
import binascii

hex_map = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']

sock = remote("oldschool.area52.airforce",9999)
#context.update(arch='amd64', log_level='debug')

sock.recvuntil("stay safe:\n")
sock.recvline()
flag = sock.recvline().strip()

print("flag = ",flag)
sock.recvuntil("?")


S_k = ['']* (2**8)
print(S_k)
for r in range(2**8):
	bin_r = "{0:b}".format(r)
	bin_r = (8-len(bin_r))*"0" + bin_r
	req = ""
	for c in bin_r:
		if c == "1":
			req+="80"
		else:
			req+="00"

	#req = binascii.hexlify(struct.pack(">B",r))
	#print(binascii.hexlify(req))
	message = '11'*8 + req
	print(bin_r, req)
	print("message of choice",message)

	sock.send(message + '\n')

	F_u = sock.recvline().strip()
	if F_u == '':
		F_u = sock.recvline().strip()[-32:]

	print("Response = ",F_u)

	for i in range(2**8):
		guess_T_L = message[16:32] #new L is old right

		#guess = struct.pack(">B",i)
		process = subprocess.Popen(("python3 test.py " + message[16:32] +" "+ str(i)).split(), stdout=subprocess.PIPE) # F(old R, key_guess)
		output, error = process.communicate() 
		pre_xor = output.strip() #application of T to message[:8], so this is what we think the R is going to be

		xs = zip(pre_xor, message[:16]) # xor with old left
		guess_T_R = ''.join([hex_map[int(a,16) ^ int(b,16)] for a,b in xs])
		#print(xs,guess_T_R)

		guess_T = guess_T_L + guess_T_R

		sock.recvuntil("?")
		#print("Sending",guess_T)
		sock.send(guess_T + "\n")
		resp = sock.recvline().strip()
		#print("got " + resp)
		#print("looking for " + F_u)
		# print(resp[:16])
		# print(F_u[16:])

		# if (resp[:16]==F_u[16:]): #random test for if a=d i guess
		# 	print("!!!!!!! a=b")
		# 	break

		#print("---")
		#print(resp[16:])
		#print(F_u[:16])
		#print("---")

		if (resp[16:32]==F_u[:16]): #is c = b?
			print("!!!!!!! c=b")
			#print(i)
			#print(flag)
			S_k[r] = i
			print(S_k)
			print("-"*30)
			break
	else:
		print("FAIL")
		sys.exit(1)

print(S_k)
print(flag)
sock.interactive()
