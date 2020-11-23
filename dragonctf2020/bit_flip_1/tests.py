from task import Rng
import task

from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Cipher import AES
import hashlib
import os
import base64
from gmpy2 import is_prime


def gen_prime(rng):
    prime = rng.getbits(512)
    iter = 0
    while not is_prime(prime): # can we theorize about in what case a series of sha256 hashes is prime?
      iter += 1
      prime = rng.getbits(512)
    print("Generated after", iter, "iterations") # we get the number of iterations, but idk how that could be helpful
    return prime

def bit_flip(x, b):
  flip_str = base64.b64decode(b)
  return task.xor32(flip_str, x)

x = 106346346346346437

print("{0:b}".format(x))
# r1 = Rng(long_to_bytes(x))
# r2 = Rng(long_to_bytes(x + 2))
# r3 = Rng(long_to_bytes(x - 2))
# r4 = Rng(long_to_bytes(x - 8))

# gen_prime(r1)
# gen_prime(r2)
# gen_prime(r3)
# gen_prime(r4)

y = long_to_bytes(x)
gen_prime(Rng(y))

# b = base64.b64encode(long_to_bytes(1))
# yb = bit_flip(y, b) # yb is either x + 1 or x - 1
# gen_prime(Rng(yb))
# print(x, bytes_to_long(yb)) # this one will be weird, because 1 is not a multiple of 2! just brute force the last bit, literally just takes 2 tries

b = base64.b64encode(long_to_bytes(2))
yb = bit_flip(y, b) # yb is either x + 2 or x - 2, depending on if that bit is 0 or 1 in the original x
print(x, bytes_to_long(yb))
gen_prime(Rng(yb))

b = base64.b64encode(long_to_bytes(4))
yb = bit_flip(y, b)
print(x, bytes_to_long(yb))
gen_prime(Rng(yb)) # this says +2 iterations, so the seed must have gone down, so the bit is 1

b = base64.b64encode(long_to_bytes(4 + 8))
yb = bit_flip(y, b)
print(x, bytes_to_long(yb))
gen_prime(Rng(yb)) # this says -2 iterations, and we know the 4 flip makes the seed go -4, so the 8 flip must make it go +8, so the net is +4 and -2 iterations
# so the 8 bit is 0

# we know the 4 flip makes it go -4
# so the 8 flip will make the total seed change be -12 or + 4
# 

b = base64.b64encode(long_to_bytes(2048))
yb = bit_flip(y, b) # yb is either x + 2048 or x - 2048, depending on if that bit is 0 or 1 in the original x
print(x, bytes_to_long(yb))
gen_prime(Rng(yb))

# r1.getbits(512)
# r1.getbits(512)
# r2.getbits(512)

# for i in range(10):
#     x = r1.getbits(512)
#     y = r2.getbits(512)
#     print(f"{x} vs {y}")
