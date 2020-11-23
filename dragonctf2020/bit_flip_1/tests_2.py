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
# Assume we know the first k bits of the seed
# 1. Flip the lowest k bits to 1 except the last bit, let i_1 = # iterations
# seed = ...1111111...0 or ...0111111...0
# 2. Flip the lowest k bits to 0, let i_2 = # iterations
# seed = ...1000... or ...0000...


# 1. Flip the lowest k bits to 1 except the last bit, let i_1 = # iterations
# s0 = ...1111111...10 or ...0111111...10
# +2
# s1 = ..f0000000...00 or ...1000000...00

# if case #1 (k+1th bit is 1) then it should match if we flip all the k bits to 0 and flip the k+1th bit
    # so the number of iterations in flip_2 should be 1 less than flip_1
# if case #2 (k+1th bit is 0) then it should be chaos

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