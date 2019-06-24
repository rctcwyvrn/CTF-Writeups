#from pwn import *
#import base64, codecs
from decimal import *
getcontext().prec = 1000
from fpylll import *



x1 = Decimal("4.1212347219384128947487124918471289")
x2 = Decimal("3.421894121421412415195812094124")
x3 = Decimal("9.858931919193194214481028491248012041249124")

bit_len = 60

c0 = Decimal("3.870489012421") * (10 ** bit_len)
c1 = Decimal("2.21481294810") * (10 ** bit_len)
c2 = Decimal("5.7482091460") * (10 ** bit_len)
c3 = Decimal("2.890904821941") * (10 ** bit_len)
c4 = Decimal("3.920482914") * (10 ** bit_len)

y1 = c0 + c1*x1 + c2*x1**2 + c3*x1**3 + c4*x1**4
y2 = c0 + c1*x2 + c2*x2**2 + c3*x2**3 + c4*x2**4
y3 = c0 + c1*x3 + c2*x3**2 + c3*x3**3 + c4*x3**4

scale = 250

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
l_red = LLL.reduction(lattice)
#print(l_red)


t = (int(y1), int(y2), int(y3), 10**bit_len, 10**bit_len, 10**bit_len, 10**bit_len,10**bit_len)
# #set_precision()
# M = MatGSO(l_red)
# _ = M.update_gso()
# E = Enumeration(M)
# _, v2 = E.enumerate(0, l_red.nrows, 5, 40, M.from_canonical(t))[0]
# v3 = IntegerMatrix.from_iterable(1, l_red.nrows, map(lambda x: int(x), v2))
# v0 = v3*A
v0 = CVP.closest_vector(l_red, t)

print("closest=",v0[3:],"given_to_compare = ",t[3:])
print("actual=",c0,c1,c2,c3,c4)

print("sanity1:",(int(v0[0])-(y1)))
print("sanity2:",(int(v0[1])-(y2)))
print("sanity3:",(int(v0[2])-(y3)))

print("check1:",(int(v0[3])-(c0)))
print("check2:",(int(v0[4])-(c1)))
print("check3:",(int(v0[5])-(c2)))
print("check4:",(int(v0[6])-(c3)))
print("check5:",(int(v0[7])-(c4)))


