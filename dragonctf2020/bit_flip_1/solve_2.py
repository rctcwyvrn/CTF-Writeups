import task
import base64
from Crypto.Util.number import bytes_to_long, long_to_bytes
from gmpy2 import is_prime
from Crypto.Cipher import AES

chal = task.Chal()
def send(bit_str, debug=True):
    if debug:
        return chal.send(bit_str)
    
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

# get started
base_iter = send("")
print(f"base iter: {base_iter}")
seed = "0" # complete guess
last = 0
for i in range(1,30):
    bit_str = base64.b64encode(long_to_bytes(2**i))
    pos_diff = 2**(i-1) 
    neg_diff = -1 * 2**(i-1)
    iters = send(bit_str)
    diff = iters - base_iter
    if diff == pos_diff: # took more iterations, number went down, bit was 1
        seed = "1" + seed
    elif diff == neg_diff:
        seed = "0" + seed
    else:
        print(f"Failed at i = {i}")
        last = i
        break

for i in range(last, 128):
    #print(seed)
    x = send(flip_1(seed))
    y = send(flip_2(seed))
    #print(f"{x} and {y}")
    if x == y + 1:
        seed = "0" + seed
    else: 
        seed = "1" + seed 
print(seed)
print(long_to_bytes(int(seed,2)))
print(chal.alice_seed)

def gen_prime(rng):
    prime = rng.getbits(512)
    iter = 0
    while not is_prime(prime): # can we theorize about in what case a series of sha256 hashes is prime?
      iter += 1
      prime = rng.getbits(512)
    #print("Generated after", iter, "iterations") # we get the number of iterations, but idk how that could be helpful
    return prime

def decode(seed):
    send(b"")
    alice_rng = task.Rng(seed)
    prime = gen_prime(alice_rng)
    alice_secret = alice_rng.getbits()
    shared = pow(chal.bob_number, alice_secret, prime)
    print(f"mine = {shared} | real = {chal.alice.shared}")
    cipher = AES.new(long_to_bytes(shared, 16)[:16], AES.MODE_CBC, IV=chal.iv)
    flag = cipher.decrypt(chal.enc_flag)
    print(f"flag! {flag}")
decode(long_to_bytes(int(seed,2)))