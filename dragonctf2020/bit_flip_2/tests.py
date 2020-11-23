# use the solution from bit flip 1 to get the seed
# manipulate the seed to get a prime that can be exploited?
# brute force from there?
# from numpy.random import randint
# from gmpy2 import is_prime

# g = 5
# goal_order = 13

# while True:
#     r = randint(100,1000)
#     if is_prime(13*r + 1):
#         break

# print(r)

# bitcoin time lmao
import task
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Cipher import AES
import hashlib
import os
import base64
from gmpy2 import is_prime
from bitcoin import get_val
from multiprocessing import Pool
import sys

# def test(i):
#     print(f"Testing #{i}")
#     seed = bytes.fromhex(get_val(i)) 
#     # seed = bytes.fromhex('14b3932c241793d366df2bab224d5789d4654ea1f25337bc46a44db595aa0fb8') 
#     # seed = bytes.fromhex('7c4dea8e47e58b2a1f8ecf9020b95df164dbfccc0f5cfff21993a1df7d0946ae') 

#     # r = task.Rng(seed)
#     # print(r.more_bytes()) 
#     # print(r.generated.hex())

#     prev = long_to_bytes(bytes_to_long(seed) - 2)
#     r = task.Rng(prev)
#     maybe_prime = r.getbits(512)
#     zero = r.getbits()

#     if is_prime(maybe_prime):
#         print("FOUND IT!")
#         print(f"{seed} | {seed.hex()} | {maybe_prime} | {prev.hex()} | check: {zero}")
#         sys.exit(0)

# p = Pool(16)
# p.map(test, range(634252, 634843))

seed = bytes.fromhex("24534c54e80ceb4c0a3f278375d389e20f3d7db8563d742f35fbac86050f227f")
r = task.Rng(seed)
p = r.getbits(512)
secret = r.getbits()
print(p, is_prime(p))
print(secret)