
# x given, a secret
def gg(tup, a, x):
	(_, p, g), n = tup, len(a) #all these are constants
	assert len(bin(x)[2:]) <= n
	X = bin(x)[2:].zfill(n) #fills with 0's until it is n bits long
	f_ax = g
	for i in range(1, n):
		f_ax *= pow(g, a[i] * int(X[i]), p) #f_ax = g ** (sum of a[i] st X[i] == 1) mod p
	return f_ax % p

x = 98199951302215711051429358164423948855 #call the given parameter x, the length variable n
(p, g) = (0xa5b80863b39a3e96d977c8643c4aee27, 0x1569cdd327ca024e697126a916e6c680) 	

# | f_a(n + 0) = 32018926747880781870818419149123000486
# | f_a(n + 1) = 220112245704810102801448451172786975350
# | f_a(n + 2) = 93961603864995523879506774294783742735
# | f_a(n + 3) = 30216000626561977313049343150984758011
# | f_a(n + 4) = 22759142941409636545517699182836380570 

#print(len(bin(x)[2:]))
for j in range(10):
	print(gg([None,p,g],[i for i in range(128)],x+j)) #we need to be able to rebuild the state array from 5 operations
