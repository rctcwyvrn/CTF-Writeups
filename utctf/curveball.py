from Crypto.Util.number import long_to_bytes, bytes_to_long
import hashlib
# x0,y0 = (int("C81E728D9D4C2F636F067F89CC14862C",16),int("31E96A93BF1A7CE1872A3CCDA6E07F86",16))
# x1,y1 = (int("ECCBC87E4B5CE2FE28308FD9F2A7BAF3",16),int("ADF6E4F1052BDE978344743CCDCF5771",16))
# x2,y2 = (int("E4DA3B7FBBCE2345D7772B0674A318D5",16),int("0668FBCFE4098FEA0218163AC21E6531",16))


x0 = 2
y0 = 5398141

x1 = 3
y1 = 5398288

x2 = 5
y2 = 5398756

m = hashlib.md5()
m.update(str(x0).encode())
print(m.hexdigest().upper())

m = hashlib.md5()
m.update(str(y0).encode())
print(m.hexdigest().upper())

m = hashlib.md5()
m.update(str(x1).encode())
print(m.hexdigest().upper())

m = hashlib.md5()
m.update(str(y1).encode())
print(m.hexdigest().upper())

m = hashlib.md5()
m.update(str(x2).encode())
print(m.hexdigest().upper())

m = hashlib.md5()
m.update(str(y2).encode())
print(m.hexdigest().upper())

# x0,y0 = 2,1942
# x1,y1 = 4,3402
# x2,y2 = 5,4414

A = x0 - x1
B = x0 - x2
C = x1 - x2

final = ((y0 * x1 * x2) / (A*B)) - ((y1 * x0 * x2) / (A*C)) + ((y2 * x0 * x1) / (B*C))
#final = final % 2**(16)
print("final = ",final,long_to_bytes(final))
print("hex = ", long_to_bytes(final).hex())

#Flag is the final-th entry in the flag list...