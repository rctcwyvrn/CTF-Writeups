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


def is_strong_prime(prime):
    strong_prime = 2*prime+1
    return not ( not (prime % 5 == 4) or not is_prime(prime) or not is_prime(strong_prime))

# def test(i):
#     # if i % 10 == 0:
#     #     print(f"Testing #{i}")
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

#     if is_strong_prime(maybe_prime):
#         print("FOUND IT!")
#         print(f"{seed} | {seed.hex()} | {maybe_prime} | {prev.hex()} | check: {zero}")
#         sys.exit(0)

# p = Pool(16)
# p.map(test, range(554843, 604843))

# """
# b'\xd6s@\x1b\x92\xc1\xe8\xa1\xf6\xf7\x8e\xd8\xc1;_\xcb\xe2n\xb4\x9c\xcaf\xa2N\x01W\xbb~HZ\x98)' 
# | d673401b92c1e8a1f6f78ed8c13b5fcbe26eb49cca66a24e0157bb7e485a9829
# | 3161267229276531497081302967686405968466737648990929359577313866219640543390720373254317588083712130837044022830796681083658913112035538624949461633371439 
# | d673401b92c1e8a1f6f78ed8c13b5fcbe26eb49cca66a24e0157bb7e485a9827 
# | check: 0
# """

seed = bytes.fromhex("e3a12ac6c8d3208d440d68c2f2574b12f84391352704713b01b822813806185f")
r = task.Rng(seed)
p = r.getbits(512)
secret = r.getbits()
print(p, is_strong_prime(p))
print(secret)

dh = task.DiffieHellman(seed)
print(dh.my_secret)