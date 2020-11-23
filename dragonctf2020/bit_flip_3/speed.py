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
seed = long_to_bytes(x)
bin_x = "{0:b}".format(x)
# 1. Flip the lowest k bits to 1 except the last bit, let i_1 = # iterations
# s0 = ...1111111...10 or ...0111111...10 
# +2
# s1 = ..f0000000...00 or ...1000000...00

# 2. Flip the low k bits to 0 and flip the k+1th bit
# s0 = ...0000000...00 or ...1000000...00

# if case #1 (k+1th bit is 0) then flip_1 should be one iteration behind flip_2 
# if case #2 (k+1th bit is 1) then it should be chaos

# now that we know the k+1th bit as well, to try and get the k+2th bit we do
# 1. flip_1
# s0 = ..11111111...10 or ..01111111...10 
# +2
# s1 = .f00000000...00 or ..10000000...00

# 2. flip_2
# s0 = ..00000000...00 or ..10000000...00

# so if the k+1th bit is 1, then we send the exact same flip_1
# last sent this:
# ...1111111...10
# need to send for the next:
# ..?1111111...10
# exactly the same :)
# flip_2 will NOT be the same if k+1 is 0 because we would have sent the last f2 = 
# ...1000000...00
# when we need
# ..10000000...00 
def flip_1(known):
    flip = 0
    for i, bit in enumerate(known[::-1]):
        if i == 0:
            if bit == "1":
               flip += 2**i 
            continue
        if bit == "0":
            flip += 2**i

    flip_str = base64.b64encode(long_to_bytes(flip))
    return flip_str

def flip_2(known):
    flip = 0
    for i, bit in enumerate(known[::-1]):
        if bit == "1":
            flip += 2**i

    flip += 2**len(known)

    flip_str = base64.b64encode(long_to_bytes(flip))
    return flip_str
x = -11
known = bin_x[x:]
print(known)
print(f"next bit = {bin_x[x-1]}")

flip_str = flip_1(known) 
res = bit_flip(seed, flip_str)
print(bin_x)
print("{0:b}".format(bytes_to_long(res)))

r1 = Rng(res)

flip_str = flip_2(known) 
res = bit_flip(seed, flip_str)
print("{0:b}".format(bytes_to_long(res)))

r2 = Rng(res)

gen_prime(r1)
gen_prime(r2)