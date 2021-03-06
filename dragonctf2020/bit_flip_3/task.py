#!/usr/bin/python3

from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Cipher import AES
import hashlib
import os
import base64
from gmpy2 import is_prime

FLAG = open("flag").read()
FLAG += (16 - (len(FLAG) % 16))*" "


class Rng:
  def __init__(self, seed):
    self.seed = seed
    self.generated = b""
    self.num = 0

  def more_bytes(self):
    self.generated += hashlib.sha256(self.seed).digest()
    self.seed = long_to_bytes(bytes_to_long(self.seed) + 1, 32)
    self.num += 256


  def getbits(self, num=64):
    while (self.num < num):
      self.more_bytes()
    x = bytes_to_long(self.generated)
    self.num -= num
    self.generated = b""
    if self.num > 0:
      self.generated = long_to_bytes(x >> num, self.num // 8)
    return x & ((1 << num) - 1)


class DiffieHellman:
  def gen_strong_prime(self):
    prime = self.rng.getbits(512)
    #print(f"first prime: {prime}")
    iter = 0
    strong_prime = 2*prime+1
    #print(f"first check {not (prime % 5 == 4) or not is_prime(prime) or not is_prime(strong_prime)}")
    while not (prime % 5 == 4) or not is_prime(prime) or not is_prime(strong_prime):
      iter += 1
      prime = self.rng.getbits(512)
      strong_prime = 2*prime+1
    #print("Generated after", iter, "iterations")
    self.iter = iter
    return strong_prime

  def __init__(self, seed, prime=None):
    self.rng = Rng(seed)
    if prime is None:
      prime = self.gen_strong_prime()

    self.prime = prime
    self.my_secret = self.rng.getbits()
    self.my_number = pow(5, self.my_secret, prime)
    self.shared = 1337

  def set_other(self, x):
    self.shared ^= pow(x, self.my_secret, self.prime)

def pad32(x):
  return (b"\x00"*32+x)[-32:]

def xor32(a, b):
  return bytes(x^y for x, y in zip(pad32(a), pad32(b)))

def bit_flip(x, s):
  #print("bit-flip str:")
  flip_str = base64.b64decode(s)
  return xor32(flip_str, x)


class Chal:
  def __init__(self):
    self.alice_seed = os.urandom(16)

  def send(self, s):
    alice = DiffieHellman(bit_flip(self.alice_seed, s))
    self.alice = alice
    bob = DiffieHellman(os.urandom(16), alice.prime)

    alice.set_other(bob.my_number)
    # print("bob number", bob.my_number)
    bob.set_other(alice.my_number)
    self.iv = os.urandom(16)
    #print(base64.b64encode(iv).decode())
    cipher = AES.new(long_to_bytes(alice.shared, 16)[:16], AES.MODE_CBC, IV=self.iv)
    self. enc_flag = cipher.encrypt(FLAG.encode())
    #print(base64.b64encode(enc_flag).decode())
    return alice.iter
