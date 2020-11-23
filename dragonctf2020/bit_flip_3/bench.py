# see how long it takes for requests to bit flip 3

import base64
from Crypto.Util.number import bytes_to_long, long_to_bytes
from gmpy2 import is_prime
from Crypto.Cipher import AES
from pwn import *
import subprocess
import time

# context.update(arch='amd64', log_level='debug')
r = remote("bitflip3.hackable.software", 1337)
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
total_sends = 0
send_times = []

def send_all(bit_str):
    global total_sends, send_times
    total_sends += 1
    start = time.time()
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
    end = time.time()
    send_times.append(end - start)
    return [iters, iv_bytes, flag_bytes]

def send(bit_str):
    return send_all(bit_str)[0]

for _ in range(30):
    send("")

print(send_times)