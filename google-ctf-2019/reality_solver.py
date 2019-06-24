from pwn import *
import base64, codecs
from decimal import *

from fpylll import *

prec = 100000
getcontext().prec = prec
#context.update(arch='amd64', log_level='debug')

s = remote("reality.ctfcompetition.com", 1337)

flag_line = s.recvline()
enc_flag = flag_line[len("Here's a base32-encoded and encrypted flag: "):]
s.recvuntil("give you 3\n")

coef_1 = s.recvline()

a = "coefficients 1: "
l = len(a)
x1, y1 = coef_1.split(",")

#x has 500 points of precision
#y also has 500 in total

x1 = Decimal(x1[l:])
y1 = Decimal(y1)

coef_2 = s.recvline()
x2, y2 = coef_2.split(",")

x2 = Decimal(x2[l:])
y2 = Decimal(y2)


coef_3 = s.recvline()
x3, y3 = coef_3.split(",")

x3 = Decimal(x3[l:])
y3 = Decimal(y3)

scale = 238

# x1 *= 10**scale
# x2 *= 10**scale
# x3 *= 10**scale

y1 *= 10**scale
y2 *= 10**scale
y3 *= 10**scale
#lattice = IntegerMatrix.from_matrix([[1,x1,x1**2,x1**3,x1**4],[1,x2,x2**2,x2**3,x2**4],[1,x3,x3**2,x3**3,x3**4],[1,0,0,0,0]])

matrix = [
[(10**scale)*1,(10**scale)*1,(10**scale)*1,1,0,0,0,0],
[(10**scale)*x1,(10**scale)*x2,(10**scale)*x3,0,1,0,0,0],
[(10**scale)*x1**2,(10**scale)*x2**2,(10**scale)*x3**2,0,0,1,0,0],
[(10**scale)*x1**3,(10**scale)*x2**3,(10**scale)*x3**3,0,0,0,1,0],
[(10**scale)*x1**4,(10**scale)*x2**4,(10**scale)*x3**4,0,0,0,0,1],
]

new_matrix = []
for column in matrix:
	new_matrix.append([int(x) for x in column])

matrix = new_matrix

lattice = IntegerMatrix.from_matrix(matrix)
#print(lattice)
print("startingLLL")
l_red = LLL.reduction(lattice)
print("doneLLL")
#print(l_red)

enc_flag = enc_flag[:-1]
print("flag=",enc_flag)
flag_bytes = base64.b32decode(enc_flag)
flag_bytes = bytes(flag_bytes)
print(flag_bytes)

# bit_len = (len(flag_bytes)*8)
# print(bit_len)
bit_len = 0
print("starting CVP")
t = (int(y1), int(y2), int(y3), 10**bit_len, 10**bit_len, 10**bit_len, 10**bit_len,10**bit_len)
v0 = CVP.closest_vector(l_red, t)
print("done CVP")
# M = gso.MatGSO(l_red)
# M.set_precision()
# _ = M.update_gso()
# E = Enumeration(M)
# _, v2 = E.enumerate(0, A.nrows, 5, 40, M.from_canonical(t))[0]
# v3 = IntegerMatrix.from_iterable(1, A.nrows, map(lambda x: int(x), v2))
# v0 = v3*A
#print(v1)

print("closest=",v0[3:],"given_to_compare = ",t[3:])

print(int(v0[0]))
getcontext().prec = 1000
print("sanity1:",(int(v0[0])/(y1)))
print("sanity2:",(int(v0[1])/(y2)))
print("sanity3:",(int(v0[2])/(y3)))
getcontext().prec = prec
#print("actual=",c0,c1,c2,c3,c4)

key = int(v0[3])
print("Key?",str(key),key)
IV = int(v0[5])
print("IV?",str(IV))
print("flag",(enc_flag))
f = open("reality_res.txt","w")
f.write(str(key)+"\n")
f.write((enc_flag)+"\n")
f.write(str(IV))
f.close()
#out = b''

# i=0
# for byte in key_bytes:
# 	print(byte,flag_bytes[i])
# 	out+=bytes([byte^flag_bytes[i]])
# 	i+=1
# print(out)