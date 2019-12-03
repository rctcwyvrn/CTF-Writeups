from pwn import *
from Crypto.Util import number
#chosen ciphertext attack, we can submit any ciphertext we want that is:
# >0
# int
# <=n
# not the ciphertext

#context.update(arch='amd64', log_level='debug')
sock = remote("squaredaway.area52.airforce", 7979)
sock.recvuntil("public key is:")

_ = sock.recvline()
_ = sock.recvline()
n = int(sock.recvline().strip())

sock.recvuntil("choice?")
sock.send("1 \n")


sock.recvuntil("ciphertext:")
_ = sock.recvline()
_ = sock.recvline()
ciphertxt = int(sock.recvline().strip())
print("goal ciphertext = ",ciphertxt)

sock.recvuntil("ciphertext?")

#sock.send(str(ciphertxt)+"\n")
blinded = (ciphertxt*4) % n
sock.send(str(blinded)+"\n")

_ = sock.recvuntil("is:")
haha = int(sock.recvline().strip(),16)
print("haha=",haha)

flag =(haha*number.inverse(2,n)) % n
print("flag = ", flag)
print("flag readable=", number.long_to_bytes(flag))
#flag{mal13ab1litY_sucK5}

#sock.interactive()

# #test = 10**200
# test = 17777

# k = (test + test*2**8)
# #assert(k*k > n)

# #print(k*k,n)
# s = (k*k) % n 
# print(s,k,n,k*k)
# #fake_ciphertxt = (k*k) % n 

# #this gives us the first two square roots
# #time to get the next two?

# sock.send(str(s)+"\n")
# #sock.interactive()

# sock.recvuntil("is:")
# t = int(sock.recvline().strip(), 16) #we sent it k^2 mod n, it should send back a square root of k with the redundancy stripped off, so it should send back test?

# h = t + t * 2**8
# print(k,h)

# print((h*h) % n == s)
# #plan: we need h*h mod n = s
# #the server will give back t for (t*t*(2**8))^2 mod n

# # k = test + test * 2^8
# # s = k*k
# # t = dec(s)
# # h = t + t*2^8