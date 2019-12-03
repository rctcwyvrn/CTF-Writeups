import math

from decimal import * 
from Crypto.Util import number

prec = 100000
getcontext().prec = prec

def sqrt(x):
	"""Finds the square root of n using binary search."""
	lo = 0
	hi = x

	while lo < hi:
		mid = (lo + hi) // 2
		if mid**2 < x:
			lo = mid + 1
		else:
			hi = mid

	return lo


def lnot(x):
	bits = bin(x)[2:]
	out = ""
	for c in bits:
		if c == "0":
			out+="1"
		else:
			out+="0"

	return int(out,2)

def adlit(x):
	l = len(bin(x)[2:])
	return (2 ** l - 1) ^ x

#answer_i = -78675816878138566369580717947271446263

#answer_p = (2**answer_k) + answer_i
#answer_q = adlit(answer_p) + const

def genadlit(nbit):
    while True:
        p = number.getPrime(nbit)
        q = adlit(p) #adlit returns the bitflip of p
        # bits_p = bin(p)[2:]
        # bits_q = bin(q)[2:]

        #print(bits_p,bits_q)
        q += const 

        #print("{} {}".format(len(bin(p)[2:]),len(bin(q)[2:])))
        print("tic")
        if number.isPrime(q):
            return p, q


def solve(n,k=0,k_diff = 0):
	print("goal=",n)

	a = 1
	b = const-1
	c = -1 * n

	d = b**2 - 4*a*c

	sol1 = (-b-sqrt(d))/(2*a)
	sol2 = (-b+sqrt(d))/(2*a)

	print(sol1,sol2)

	if k == 0:
		k = round(math.log(sol2,2)) + k_diff

	#k = answer_k - 1

	#print("k check",k,answer_k)
	# assert(answer_k == k)

	p = 2**k
	q = adlit(p) + const

	print("test p,q",p,q)
	print("make sure this is equal to q=",2**k+const-1) #so this formula is correct, q formula is correct

	test_n = (2**k * (2**k + const-1))

	assert(test_n == p*q)

	print("fancy one",test_n)
	print("goal=",n)

	print("testdiff, should be 6",p*q - (p+2)*(adlit(p+2)+const) + 2*const)

	diff = test_n - n # diff = arth series up to i - i*const = i^2 + (1-const)i - diff 
	print("diff = ",diff)

	#assert(test_n > n)


	a = 1
	b = 1 - const
	c = -1 * diff

	d = Decimal(b**2 - 4*a*c)

	sol1_new = (-b-sqrt(d))/(2*a)
	sol2_new = (-b+sqrt(d))/(2*a)

	#print(d,sol1,sol2,-b+sqrt(d))

	i = sol2_new

	# a = 1
	# b = 2**(k+1)
	# c = -diff

	# d = Decimal(b**2 - 4*a*c)

	# sol1_new = (-b-sqrt(d))/(2*a)
	# sol2_new = (-b+sqrt(d))/(2*a)

	#print(sol1,sol2)

	#i = sol2_new

	#print("found i = {}, answer_i = {}, diff = {}".format(i,answer_i, i-answer_i))
	#print("arth. series with i={} terms ".format(i))

	prime_p = (p+i)
	prime_q = adlit(int(prime_p)) + const

	print("arth. series with i={} terms ".format(i))

	return prime_p, prime_q
	
const = 31337
if __name__ == "__main__":
	global answer_p, answer_q, n, answer_k
	const = 31337
	answer_k = 256
	answer_p, answer_q = genadlit(answer_k)
	print("primesgenerated")
	#print("i = ",answer_p - 2**(answer_k))
	#i = -78675816878138566369580717947271446263
	#n = 20582109025288917636046539634425125826468498243242091686946142548308862411607
	print("answer p=",answer_p)

	print("primeness = ",number.isPrime(answer_p),number.isPrime(answer_q))
	n = answer_p * answer_q
	good = False
	k_diff = 3
	while not good:
		try:
			if k_diff == -3:
				print("failed")
				break

			print("KDIFF = {} ---------------------------------------------".format(k_diff))
			prime_p, prime_q = solve(n,k_diff)
			k_diff-=1
			print("we calculate that p was=",prime_p)
			print("p wrong by",prime_p - answer_p )
			print("q wrong by", prime_q - answer_q)

			print(number.isPrime(int(prime_p)),number.isPrime(int(prime_q)))


			e = 65537
			flag = b'maowmaowmaow'
			c = pow(number.bytes_to_long(flag), e, n)
			answer_priv = number.inverse(e,(answer_p-1)*(answer_q-1))


			actual = pow(c,answer_priv,n)
			print("actual flag=",actual)
			print(number.long_to_bytes(actual))

			for pub_guess in [3,5,7,11,17,65537]:
				#print(number.isPrime(prime_p),number.isPrime(prime_q))

				priv_key = number.inverse(pub_guess,(prime_p-1)*(prime_q-1))

				print("priv = ",priv_key, "actual=",answer_priv)
				print("diff =",priv_key-answer_priv)

				try:
					flag = pow(c,priv_key,n)

					print("flag=",flag)
					print(number.long_to_bytes(flag))

					good = (flag - actual == 0)
					if good:
						print("success tmtm")
						break
				except InvalidOperation:
					pass
		except TypeError:
			pass
# if not (p+i - answer_p == 0.0):
# 	print("try again-----------------------------")
# 	i = const - sol2_new - 1
# 	prime_p = int(p+i)
# 	prime_q = adlit(prime_p)
# 	print("arth. series with i={} terms ".format(i))
# 	print("we calculate that p was=",prime_p)
# 	print("p wrong by",prime_p - answer_p )
# 	print("q wrong by",prime_q - answer_q )
