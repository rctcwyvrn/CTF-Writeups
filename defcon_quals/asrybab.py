from pwn import *
import pow
import marshal

def solve_baby_RSA(n,e,v):
	print("solving")


#test = marshal.dumps(solve_baby_RSA)



context.update(arch='amd64', log_level='debug')
s = remote('asrybab.quals2019.oooverflow.io', 1280)
_ = s.recvline()
c = s.recvline()

challenge = c.split()[1]
print(challenge)

n = s.recvline()

num = n.split()[1]
print(num)

print("starting solve")
ret = str(pow.solve_pow(challenge,int(num)))
print("completed solve")

ret +="\n"
s.send(ret)

#s.interactive()

_ = s.recvline()

aa = "1\n"
s.send(aa)

_ = s.recvline()

aa = "1\n"
s.send(aa)

_ = s.recvline()

aa = "1\n"
s.send(aa)

_ = s.recvline()

n1 = s.recvline()
e1 = s.recvline()
v1 = s.recvline()

n2 = s.recvline()
e2 = s.recvline()
v2 = s.recvline()

n3 = s.recvline()
e3 = s.recvline()
v3 = s.recvline()

time =s.recvline()
hex_digest = s.recvline()



s.close()

chal_1 = [n1,e1,v1]

chal_2 = [n2,e2,v2]

chal_3 = [n3,e3,v3]

print(chal_1)
print(time)
print(hex_digest)


s = remote('asrybab.quals2019.oooverflow.io', 1280)
_ = s.recvline()
c = s.recvline()

challenge = c.split()[1]
print(challenge)

n = s.recvline()

num = n.split()[1]
print(num)

print("starting solve")
ret = str(pow.solve_pow(challenge,int(num)))
print("completed solve")

ret +="\n"
s.send(ret)
aa="2\n"

_ = s.recvline() #welcome
s.send(aa)
_ = s.recvline()#option1
_ = s.recvline()#option2
s.send(aa)


for i in range(3):
	#it checks that s^e mod n is = v
	#so the s st s^e = v + k*n for some k
	#if this was the same as RSA then we can recover S from v 
	# s = v^(private key) mod n
	s.send(str(i)+"\n")


	#so continuing the RSA stuff
	#n_rsa = pq
	#n = toitent = (p-1)(q-1)
	#private key = d st d*e mod n = 1

s.send(n1) #modulus			->these two come from the create_key method
s.send(e1) #public key
s.send(v1) #ciphertext		->this one is a random number with 0 to 1279 bits
s.send(n2)
s.send(e2)
s.send(v2)
s.send(n3)
s.send(e3)
s.send(v3)

s.send(time)
s.send(hex_digest)

while True:
	_ = s.recvline()
s.interactive()