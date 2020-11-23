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

  # generate 256 more bits onto self.generated
  def more_bytes(self):
    #print(f"seed: {self.seed}")

    self.generated += hashlib.sha256(self.seed).digest() # longer and longer bytes of sha256
    # generated = s(seed) + s(seed + 1) + s(seed + 2) ... 
    self.seed = long_to_bytes(bytes_to_long(self.seed) + 1, 32) # pads to a multiple of 32 bytes (?)
    self.num += 256 # number of bits in generated


  # return a num-bit number
  def getbits(self, num=64): # when generating secrets it requests less than 256, so it uses the self.num > 0 code in that case
    while (self.num < num):
      self.more_bytes()
    
    # doesnt this assume self.num = num? What happens if its slightly off? I guess the code only requests getbits with multiples of 256
    x = bytes_to_long(self.generated)
    self.num -= num
    self.generated = b""

    #jk, it regenerates generated from x, using something that's a bit sketch
    if self.num > 0:
      # makes self.generated from the parts of x that arent used
      self.generated = long_to_bytes(x >> num, self.num // 8) # pads to self.num // 8
    return x & ((1 << num) - 1) # make sure x is the correct bit length, by and-ing it with 0xffffffffff


class DiffieHellman:
  # prime = bytes_to_long(s(alice_seed + iter) + s(s(alice_seed + iter + 1)))
  def gen_prime(self):
    prime = self.rng.getbits(512)
    iter = 0
    while not is_prime(prime): # can we theorize about in what case a series of sha256 hashes is prime?
      iter += 1
      prime = self.rng.getbits(512)
    # print("Generated after", iter, "iterations") # we get the number of iterations, but idk how that could be helpful

    self.iter = iter
    return prime

  def __init__(self, seed, prime=None):
    self.rng = Rng(seed)
    if prime is None:
      prime = self.gen_prime()
      #print(f"prime: {prime}")

    self.prime = prime # modulus
    self.my_secret = self.rng.getbits() # 8 byte secret int
    self.my_number = pow(5, self.my_secret, prime) # mixed value, pow(5, secret, prime)
    self.shared = 1337 # temporary value

  def set_other(self, x):
    self.shared ^= pow(x, self.my_secret, self.prime) # generate shared key

# pads to 32 bytes
def pad32(x):
  return (b"\x00"*32+x)[-32:] # prepends with null bytes

def xor32(a, b):
  return bytes(x^y for x, y in zip(pad32(a), pad32(b))) # flip

def bit_flip(x, s):
  flip_str = base64.b64decode(s)
  #print(f"bit-flip str: {flip_str}")
  res = xor32(flip_str, x)
  #print(f"flipped {bytes_to_long(x)} to {bytes_to_long(res)}")
  return res


# this is in a while loop, so we get as many attempts as we want at figuring out how to manipulate alice_seed to be something that generates a weak prime
# bad prime in this case would be so that 5 has low order in the mod p group
# is there any good way to do this that doesn't involve just brute force?

# alternatively is there a way to recover alice's seed from the information that gets leaked? 

# what information is leaked?
# - timing information?
    # - please no
# - number of iterations to get a prime
    # - doesn't work to recover the entire secret because trying to bitflip and vary this ends up moving the seed too much and you only get a few bits of the seed
# - bobs number (?)
    # - contains basically no useful information about alices secret, unless there's some way to extract the modulus prime out of it

# problems/leads
# - we have full control over the upper 16 bytes of the seed, how can we use that?
# - how do we determine when we've hit a bad prime from bobs number??
# - we get the number of iterations, so we can use that to rerun the prime generation ourselves, to try and guess the seed, or at least confirm that we're correct
#   - check if bytes_to_long(s(alice_seed + iter) + s(alice_seed + iter + 1)) is prime


# how can we get the shared value?
# - we only ever see bob.my_number, so we could theoretically pull bob.secret out of that if the prime is bad and the dlog is easy
# - but we literally never see anything to do with alice.secret, so we need to manipulate the rng in such a way that we can determine alice.secret?
# - we also never see the modulus prime, so we need to determine that as well from the rng

# is there a way to solve this that doesnt involve getting the shared value? I don't think so, the best we can do is get a bunch of ciphertexts encrypted with random keys

# alice_seed -> alice.prime and alice.secret
  # if we don't change any bits, then all of alice's values stay the same
# bob_seed -> bob.secret

class Chal:
  def __init__(self):
    self.alice_seed = os.urandom(16)
    print("{0:b}".format(bytes_to_long(self.alice_seed))) #DEBUG
  
  def send(self, bit_flip_str):
    # alice gets a 32 byte seed prepended with null bytes and bit flipped
    alice = DiffieHellman(bit_flip(self.alice_seed, bit_flip_str)) # !!! we get to bit flip alice's seed (xors the random seed with the base64 string we send)
    self.alice = alice
    # bob gets a 16 byte seed
    bob = DiffieHellman(os.urandom(16), alice.prime) # bob gets his own random 16 byte seed, but gets alice's prime, so the seed is only used to generate his secret

    alice.set_other(bob.my_number)
    # print("bob number", bob.my_number) # bob sends message to alice, shown
    self.bob_number = bob.my_number
    bob.set_other(alice.my_number) # alice sends message to alice, not shown

    self.iv = os.urandom(16)
    # print(base64.b64encode(iv).decode()) # print the IV
    
    cipher = AES.new(long_to_bytes(alice.shared, 16)[:16], AES.MODE_CBC, IV=self.iv)
    self.enc_flag = cipher.encrypt(FLAG.encode())
    # print(base64.b64encode(enc_flag).decode()) # encrypt the flag with CBC and alice's shared key value, and then base64 it and print it

    return alice.iter
