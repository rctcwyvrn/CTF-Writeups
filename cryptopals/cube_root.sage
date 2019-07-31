from Crypto.Util import number

f = open("cube_root_me.txt")
r = int(f.readlines()[0])
x = r ** (1/3) #sage is magic
#x = r ** (1/11)
print("x=",x)
print("message = ",number.long_to_bytes(x))