#time to actually factor the modulus
from pwn import *
from Crypto.Util import number
import fractions, sys

sock = remote("squaredaway.area52.airforce", 7979)
sock.recvuntil("public key is:")

_ = sock.recvline()
_ = sock.recvline()
n = int(sock.recvline().strip())

sock.recvuntil("choice?")
sock.send("1 \n")


def solve(x,s,other):
	other_b = number.long_to_bytes(other)
	h_b = other_b + other_b[-1]
	h = number.bytes_to_long(h_b)

	print(pow(h,2,n) == s)
	print(h==x)

	#gcd(k-h,n) = p" or "gcd(k-h,n) = q

	p = fractions.gcd((x - h) % n ,n)
	q = fractions.gcd((h - x) % n ,n)
	print(p,q)
	print(p*q == n)
	sys.exit(1)

	
	# print("starting solve")
	# x_p = x+1

	# while fractions.gcd(x_p-x,n) == 1:
	# 	x_p +=1
	# 	if (x_p - x) % 10000 == 0:
	# 		print(x_p)

	# print(x_p,x,n)
	# print(fractions.gcd(x_p-x,n))
	# sys.exit(1)


def test(x):
	sock.recvuntil("ciphertext?")
	print("testing ",x)

	s = pow(x,2,n)
	print("sending ",s)
	sock.send(str(s) + "\n")

	line = sock.recvline()
	print(line)
	if not "redundancy" in line:
		ptxt_str = line.strip().split()[3]
		ptxt_int = int(ptxt_str,16)
		print("got ptxt int back = ", ptxt_int)
		solve(x,s,ptxt_int)
	else:
		print("Failed redundancy")
		return False

i = 12512
while True:
	if test(i + 12498124012489124*(i+1)):
		break
	else:
		i+=12


sock.interactive()