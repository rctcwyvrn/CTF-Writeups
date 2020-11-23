import task
import base64
from Crypto.Util.number import bytes_to_long, long_to_bytes
from gmpy2 import is_prime
from Crypto.Cipher import AES
from pwn import *
import subprocess

# context.update(arch='amd64', log_level='debug')
r = remote("bitflip2.hackable.software", 1337)
pow_str = r.recvline().decode().strip()[-8:]
cmd = ["hashcash", "-mb28", pow_str]
#cmd = ["echo", "hashcash token: 1:28:201121:yxhgzzbb::AQSupovZngkT3Ubo:00000000JmvqV"]
print(cmd)

p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
p.wait()
for line in p.stdout:
    print(line)
    line = line.decode()
    if "hashcash token" in line:
        proof = line[len("hashcash token: "):]
    else:
        proof = line
    print(proof)
    r.send(proof.encode())
    break

#chal = task.Chal()
def send_all(bit_str):
    r.recvuntil("bit-flip str:")
    #r.clean()
    r.sendline(bit_str)
    r.recvline()
    iter_line = r.recvline().decode()
    iters = int(iter_line.split()[2].strip())

    # bob_line = r.recvline().decode()
    # bob_num = int(bob_line.split()[2].strip())

    iv_line = r.recvline().decode()
    iv_bytes = base64.b64decode(iv_line.strip())

    flag_line = r.recvline().decode()
    flag_bytes = base64.b64decode(flag_line.strip())

    #print(f"sent: {bit_str} || got: {iters} | {bob_num} | {iv_bytes} | {flag_bytes}")
    #print(f"DEBUG: {chal.send(bit_str)}")

    #return [iters, bob_num, iv_bytes, flag_bytes]
    return [iters, iv_bytes, flag_bytes]

def send(bit_str):
    return send_all(bit_str)[0]

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

def gen_prime(rng):
    prime = rng.getbits(512)
    iter = 0
    while not is_prime(prime): # can we theorize about in what case a series of sha256 hashes is prime?
      iter += 1
      prime = rng.getbits(512)
    #print("Generated after", iter, "iterations") # we get the number of iterations, but idk how that could be helpful
    return prime

def calculate_flips(seed):
    goal = bytes.fromhex("24534c54e80ceb4c0a3f278375d389e20f3d7db8563d742f35fbac86050f227f")
    bits_1 = "{0:b}".format(bytes_to_long(seed))
    bits_1 = "0"*(32*8 - len(bits_1)) + bits_1

    bits_2 = "{0:b}".format(bytes_to_long(goal))
    bits_2 = "0"*(32*8 - len(bits_2)) + bits_2

    #print(bits_1)
    #print(bits_2)
    flips = ""
    for b1, b2 in zip(bits_1, bits_2):
        if b1 != b2:
            flips += "1"
        else:
            flips += "0"
    #print(flips)
    flips = long_to_bytes(int(flips,2))
    flip_str = base64.b64encode(flips)

    print(f"orig: {seed.hex()} | goal: {goal.hex()} | result of flips: {task.bit_flip(seed, flip_str).hex()}")
    return flip_str

# def decode(seed):
#     send_all(calculate_flips(seed))
#     shared = 1336
#     print(f"mine = {shared} | real = {chal.alice.shared}")
#     print(f"alice: {chal.alice.prime} | {chal.alice.my_secret} | {chal.alice.my_number}")
#     cipher = AES.new(long_to_bytes(shared, 16)[:16], AES.MODE_CBC, IV=chal.iv)
#     flag = cipher.decrypt(chal.enc_flag)
#     print(f"flag! {flag}")

def decode(seed):
    [iters, iv_bytes, flag_bytes] = send_all(calculate_flips(seed))
    shared = 1336
    print(f"mine = {shared} | real = ??")
    cipher = AES.new(long_to_bytes(shared, 16)[:16], AES.MODE_CBC, IV=iv_bytes)
    flag = cipher.decrypt(flag_bytes)
    print(f"flag! {flag}")

# get started
base_iter = send(" ")

print(f"base iter: {base_iter}")
seed = "0" # complete guess
last = 0
for i in range(1,30):
    # sleep(1)
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
        print(f"Failed at i = {i} | expected {pos_diff}/{neg_diff} | got {diff} instead")
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
#print(chal.alice_seed)
decode(long_to_bytes(int(seed,2)))


### JUST COPY PASTA
base_iter = send(" ")

print(f"base iter: {base_iter}")
seed = "1" # guess the other one lmao
last = 0
for i in range(1,30):
    # sleep(1)
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
        print(f"Failed at i = {i} | expected {pos_diff}/{neg_diff} | got {diff} instead")
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
#print(chal.alice_seed)
decode(long_to_bytes(int(seed,2)))