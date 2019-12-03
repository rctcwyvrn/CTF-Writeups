from decimal import *
import math,codecs
from Crypto.Util import number
import f

#prec = 1000000000000000000
getcontext().prec = 9999

def adlit(x):
    l = len(bin(x)[2:])
    return (2 ** l - 1) ^ x


n = int("0x3ff77ad8783e006b6a2c9857f2f13a9d896297558e7c986c491e30c1a920512a0bad9f07c5569cf998fc35a3071de9d8b0f5ada4f8767b828e35044abce5dcf88f80d1c0a0b682605cce776a184e1bcb8118790fff92dc519d24f998a9c04faf43c434bef6c0fa39a3db7452dc07ccfced9271799f37d91d56b5f21c51651d6a9a41ee5a8af17a2f945fac2b1a0ea98bc70ef0f3e37371c9c7b6f90d3d811212fc80e0abcd5bbefe0c6edb3ca6845ded90677ccd8ff4de2c747b37265fc1250ba9aa89b4fd2bdfb4b4b72a7ff5b5ee67e81fd25027b6cb49db610ec60a05016e125ce0848f2c32bff33eed415a6d227262b338b0d1f3803d83977341c0d3638f",16)
c_goal = int("0x2672cade2272f3024fd2d1984ea1b8e54809977e7a8c70a07e2560f39e6fcce0e292426e28df51492dec67d000d640f3e5b4c6c447845e70d1432a3c816a33da6a276b0baabd0111279c9f267a90333625425b1d73f1cdc254ded2ad54955914824fc99e65b3dea3e365cfb1dce6e025986b2485b6c13ca0ee73c2433cf0ca0265afe42cbf647b5c721a6e51514220bab8fcb9cff570a6922bceb12e9d61115357afe1705bda3c3f0b647ba37711c560b75841135198cc076d0a52c74f9802760c1f881887cc3e50b7e0ff36f0d9fa1bfc66dff717f032c066b555e315cb07e3df13774eaa70b18ea1bb3ea0fd1227d4bac84be2660552d3885c79815baef661",16)
#n = 1606938044258990275541962132064261811273999509086615679339600
#n_init = 0x3ff77ad8783e006b6a2c9857f2f13a9d896297558e7c986c491e30c1a920512a0bad9f07c5569cf998fc35a3071de9d8b0f5ada4f8767b828e35044abce5dcf88f80d1c0a0b682605cce776a184e1bcb8118790fff92dc519d24f998a9c04faf43c434bef6c0fa39a3db7452dc07ccfced9271799f37d91d56b5f21c51651d6a9a41ee5a8af17a2f945fac2b1a0ea98bc70ef0f3e37371c9c7b6f90d3d811212fc80e0abcd5bbefe0c6edb3ca6845ded90677ccd8ff4de2c747b37265fc1250ba9aa89b4fd2bdfb4b4b72a7ff5b5ee67e81fd25027b6cb49db610ec60a05016e125ce0848f2c32bff33eed415a6d227262b338b0d1f3803d83977341c0d3638f
#c = 0x2672cade2272f3024fd2d1984ea1b8e54809977e7a8c70a07e2560f39e6fcce0e292426e28df51492dec67d000d640f3e5b4c6c447845e70d1432a3c816a33da6a276b0baabd0111279c9f267a90333625425b1d73f1cdc254ded2ad54955914824fc99e65b3dea3e365cfb1dce6e025986b2485b6c13ca0ee73c2433cf0ca0265afe42cbf647b5c721a6e51514220bab8fcb9cff570a6922bceb12e9d61115357afe1705bda3c3f0b647ba37711c560b75841135198cc076d0a52c74f9802760c1f881887cc3e50b7e0ff36f0d9fa1bfc66dff717f032c066b555e315cb07e3df13774eaa70b18ea1bb3ea0fd1227d4bac84be2660552d3885c79815baef661
#n = n_init
print("goal=",n)

good = False
k_diff = 3
p_guesses = [5,11,17,257,65537,4294967297,18446744073709551617] + [2*i+1 for i in range(10,2000)]
#p_guesses = [31337,65537]
flags = []
failed= 0
skipped =[]
while not good:
	#if k_diff < -3:
		#print("failed")
		#break

	#k_diff-=1
	# k_diff = 0
	# print("KDIFF = {} ---------------------------------------------".format(k_diff))
	# prime_p, prime_q = f.solve(n,k_diff = k_diff)
	prime_p, prime_q = f.solve(n)

	prime_p = int(prime_p)
	prime_q = int(prime_q)
	print("we calculate that p was=",prime_p)
	#print("p wrong by",prime_p - answer_p )
	#print("q wrong by", prime_q - answer_q)

	#removed the extra try/catch stuff for testing differen k_diffs
	#tests
	m = b'CCTF{maowmaowmaowwwwwwwwwwwwwwwwww}'
	c = pow(number.bytes_to_long(m),3,n)
	priv = number.inverse(3,(prime_p-1)*(prime_q-1))
	print("test that i have the right keys",number.long_to_bytes(pow(c,priv,n)))

	if number.isPrime(int(prime_p)) and number.isPrime(int(prime_q)):
		assert(int(prime_p) * int(prime_q) == n)
		print("THE PRIMES---------------------------------------------------------------")
		print("p = ",prime_p)
		print("q= ",prime_q)
		for p_guess in p_guesses:

			print("testing e=",p_guess)
			priv_key = number.inverse(p_guess,(prime_p-1)*(prime_q-1))

			#sanity check
			skip = False
			m = b'CCTF{maowmaowmaowwwwwwwwwwwwwwwwww}'
			c = pow(number.bytes_to_long(m),p_guess,n)
			print("sanity", number.long_to_bytes(pow(c,priv_key,n)), m)
			if not (number.long_to_bytes(pow(c,priv_key,n)) == m):
				skip = True
				skipped.append(p_guess)

			if not skip:
				#print(number.isPrime(prime_p),number.isPrime(prime_q))

				#print("priv = ",priv_key)

				flag = pow(c_goal,priv_key,n)

				#print("flag=",flag)
				#print(number.long_to_bytes(flag))
				flags.append((p_guess,number.long_to_bytes(flag)))

				if b'CCTF' in number.long_to_bytes(flag):
					print("FOUDNDOFUDFODUFDOFUDFODUFDUOND IT")
					assert(False)
				#flags.append(("key",number.long_to_bytes(priv_key)))

				#flag = int(flag)
				#flags.append(flag.to_bytes(256,byteorder='big'))

				#alt = hex(int(flag))[2:].encode()
				#print("hex=",alt)
				#flags.append(alt)


	else:
		print("failed") #this is irreleevant now :)
		failed+=1
	break

for flag in flags:
	print(flag)
	print("base64",codecs.encode(flag[1],'base64'))
	if b'CCTF' in flag[1]:
		print("FOUDNDOFUDFODUFDOFUDFODUFDUOND IT YEET")
		assert(False)

	#print("utf-8",flag[1].decode('ascii'))
	#print("ascii",codecs.encode(flag[1],'ascii'))
print(skipped)
#print(failed)


# print("v2 --------------------------")
# i = const - sol2 - 1
# print("arth. series with i={} terms ".format(i))
# print("we calculate that p was=",2**(k)+i)
# #print("wrong by",p+i - answer_p )

# prime_p = int(p+i)
# prime_q = adlit(prime_p)

# toit = (prime_p-1) *(prime_q-1)
# priv_key = number.inverse(pub_guess,toit)


# flag = pow(c,priv_key,n)

# print("flag=",flag)
# print(number.long_to_bytes(flag))
