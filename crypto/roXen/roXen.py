#!/usr/bin/env python

from Crypto.Util.number import *
#from secret import exp, flag, nbit

def lnot(x):
	bits = bin(x)[2:]
	out = ""
	for c in bits:
		if c == "0":
			out+="1"
		else:
			out+="0"

	return int(out,2)

exp = 3
flag = b'flag is gone'
nbit = 128

assert exp & (exp + 1) == 0

def old_adlit(x):
    l = len(bin(x)[2:])
    return (2 ** l - 1) ^ x

def adlit(x):
    l = len(bin(x)[2:]) #l= bitlen of x, which is nbit
    a = (2 ** l - 1) 
    bits_a = bin(a)[2:]
    #print("a",bits_a)

    b = a ^ x #returns (2**l -1) XOR p, so p and q are bitflips of each other

    bits_b = bin(b)[2:]
    #print("b",bits_b)

    test = lnot(x)
    bits_t = bin(test)[3:]
    #print(bits_t)
    #print("t", bits_t)


    bits_x = bin(x)[2:]
    # print("x",bits_x)

    for b1,b2 in zip(bits_t[::-1],bits_b[::-1]):
    	#print(b1,b2)
    	if not b1 == b2:
    		print(b1,b2)
    		break

    #print(a,b,x)
    return b
    # (l-1 bit number) ^ p
    #returns a p*(l-1) bit number, which is huge compared to the other one

def genadlit(nbit):
    while True:
        p = getPrime(nbit)
        q = adlit(p) #adlit returns the bitflip of p
        bits_p = bin(p)[2:]
        bits_q = bin(q)[2:]

        #print(bits_p,bits_q)
        q += 31337 

        #print("{} {}".format(len(bin(p)[2:]),len(bin(q)[2:])))
        if isPrime(q):
            return p, q


# a = 1241241192
# b = adlit(a)
# c = lnot(a)
# assert(b == c)

# bits_a = bin(a)[2:]
# bits_b = bin(b)[2:]

# print(bits_a,bits_b)


p, q = genadlit(nbit)

t = q - 31337

e, n = exp, p * q

c = pow(bytes_to_long(flag), e, n) #so this is RSA enc

print('n =', hex(n))
print('c =', hex(c))