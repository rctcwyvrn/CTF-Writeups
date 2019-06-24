import json#, urllib2
#from pwn import *
import requests
import random
import math
#context.update(arch='amd64', log_level='debug')

def rotate_45(qubit):
  return qubit * complex(0.707, -0.707)

flag = "U2FsdGVkX19OI2T2J9zJbjMrmI0YSTS+zJ7fnxu1YcGftgkeyVMMwa+NNMG6fGgjROM/hUvvUxUGhctU8fqH4titwti7HbwNMxFxfIR+lR4=" #aes-256-cbc

#We are alice in this situation

#Generate two strings of bits a and b that are 512 bits long
a = random.randint(0,2**512-1)
b = random.randint(0,2**512-1)

a_bits = "{0:b}".format(a)
a_bits = (512-len(a_bits))*"0" + a_bits

b_bits = "{0:b}".format(b)
b_bits = (512-len(b_bits))*"0" + b_bits

assert(len(a_bits) == 512 and len(b_bits) == 512)

qbits = []

zero_zero = {

	'real': 1,

	'imag': 0

}

one_zero = {

	'real': 0,

	'imag': 1

}

one_one = {

	'real': 1/math.sqrt(2),

	'imag': -1/math.sqrt(2)

}

zero_one = {

	'real': 1/math.sqrt(2),

	'imag': 1/math.sqrt(2)

}

for i in range(512):
	if b_bits[i] == "0":
		if a_bits[i] == "0":
			qbits.append(zero_zero)
		else:
			qbits.append(one_zero)
	else:
		if a_bits[i] == "0":
			qbits.append(zero_one)
		else:
			qbits.append(one_one)

basis = []

for i in range(512):
	if b_bits[i] == "0":
		basis.append("+")
	else:
		basis.append("x")

#print(dump_basis,dump_qbits)
#send to qbits and base server


sending = {
	'basis':basis,
	'qubits':qbits
}
#print(sending)
#headers = {'Content-type':'application/json'}

req= requests.post('https://cryptoqkd.web.ctfcompetition.com/qkd/qubits',json=sending)

print(req.status_code)
print(req.text)

json_response = req.text

data = json.loads(json_response)

response_basis = data['basis']
response_annon = data['announcement']


#404c368bf890dd10abc3f4209437fcbb 	example key
#a42da49ea19ea023d7a91ace9ae51b0b

anon_int = int(response_annon,16)
to_keep = "{0:b}".format(anon_int)

print("server response bitlen=",len(to_keep))
to_keep = (128-len(to_keep))*"0" + to_keep

out = ""
for i in range(512):
	if response_basis[i] == basis[i]:
		out+=a_bits[i]


print("shared secret =",out)
res = ""
print("Computing shared_secret XOR announcement")
for i in range(128):
	if (out[i] == "0" and to_keep[i] == "0") or (out[i] == "1" and to_keep[i] == "1"):
		res+="0"
	else:
		res+="1"

key = int(res,2)
print("key = ",key)
print("as hex:",hex(key))
#946cff6c9d9efed002233a6a6c7b83b1