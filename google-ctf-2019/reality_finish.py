import base64,math
from Crypto.Cipher import AES
#import set_2

def fixed_xor(raw1, raw2):
	out = b''
	for i in range(len(raw1)):
		out += bytes([raw1[i] ^ raw2[i]])
	return out

def blockify(in_bytes, block_size):
	blocks = []
	x = 0;
	for i in range(math.floor(len(in_bytes) / block_size)):
		blocks.append(take_block(in_bytes, x, x+block_size))
		x+=block_size
	return blocks

def take_block(in_bytes, a, b):
	out = b''
	for i in range(a,b):
		out+=bytes([in_bytes[i]])
	return out


def aes_block_dec(enc, key):
	#enc = pad(enc,16)
	aes = AES.new(key, AES.MODE_ECB)
	return aes.decrypt(enc)

def aes_cbc_mode_dec(in_bytes, IV, key):
	blocks = blockify(in_bytes,16)
	out = b''
	for block in blocks:
		last = fixed_xor(aes_block_dec(block,key),IV)
		IV = block
		out +=last
		print("CBC:mid",out)
	return out


f = open("reality_res.txt")

key_int = int(f.readline().strip())
flag = f.readline().strip()
IV_int = int(f.readline().strip())
flag_bytes = base64.b32decode(flag)
#flag_bytes = bytes(flag_bytes)

key = key_int.to_bytes(32,byteorder='big')
print(flag_bytes,key)

print(len(flag_bytes),len(key))

out = b''
i = 0
for byte in key:
	out+=bytes([byte ^ flag_bytes[i]])
	i+=1

print("straight XOR",out)

key = key_int.to_bytes(16,byteorder='big')
#IV = IV_int.to_bytes(16,byteorder='big')
IV = b'\x00'*16
#IV = key_int.to_bytes(16,byteorder='little')
print(key)
res = aes_cbc_mode_dec(flag_bytes,IV,key)

print("CBC",res)
#print(len(b'y0ur-Re4l-4Real}'))
#CTF{y0u-kn0w-y0ur-Re4l-4Real}