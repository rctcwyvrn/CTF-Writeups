import set_3, set_2, set_1
from os import urandom
import math
from base64 import b64decode
import random
import codecs

import sha1, fake_sha1 #Credit: https://github.com/ajalt/python-sha1
import md4, fake_md4 #credit:Ben Wiederhake

import sys
import time
import urllib.request

import binascii


the_key = urandom(16)
the_nonce = 100

def ctr_encrypt_me(file):
	plain_text = b''
	for line in file:
		plain_text += line.encode('ascii')

	return set_3.aes_ctr_mode_enc(plain_text,the_nonce,the_key)

def edit(ciphertext, key, offset, new_bytes):
	block_count = math.floor(offset/16)
	keystream = b''
	nonce = set_3.i2b(the_nonce)
	while len(keystream) < len(new_bytes):
		block = nonce + set_3.i2b(block_count)
		keystream += set_2.aes_block_enc(block, key)
		block_count+=1
	return ciphertext[0:offset] + set_1.fixed_xor(new_bytes, keystream) + ciphertext[offset+len(new_bytes):]


magic_key = urandom(16)
magic_nonce = random.randint(0,1000)

def ctr_magic_encrypt(plain_text):
	magic = "comment1=cooking%20MCs;userdata=" + plain_text.replace(";","").replace("=","") + ";comment2=%20like%20a%20pound%20of%20bacon"
	to_encrypt = magic.encode('ascii')
	return set_3.aes_ctr_mode_enc(to_encrypt, magic_nonce, magic_key)

#Note: I got stuck on this challenge because I was decrypting the bytes into ascii, which doesn't work 
#because the bit flipping attack results in a completely messed up block that can't be converted into ascii
def ctr_magic_decrypt(enc_bytes):
	text = set_3.aes_ctr_mode_dec(enc_bytes,magic_nonce, magic_key)
	print(text)
	if b';admin=true;' in text:
		print("admin access granted!")
		return True
	return False

#Send it A xor B, B containing text that would have been removed
#it returns A xor B xor C
#xor that with A to get B xor C
#send that back and it then decodes to B, even if B includes bad bad things, like an admin token
def challenge_26():
	secret_sauce = set_1.fixed_xor(b';admin=true;', b'A'*12)
	payload = codecs.decode(secret_sauce,'ascii')
	print(payload)
	to_flip = ctr_magic_encrypt(payload)

	changed = set_1.fixed_xor(to_flip[32:44], b'A'*12)

	res = b''
	res+= to_flip[0:32]
	res+=changed
	res+= to_flip[44:]

	test = ctr_magic_decrypt(res)


magic_key = urandom(16)

def cbc_bad_encrypt(plain_text):
	print("key being used=",magic_key)
	magic = plain_text.replace(";","").replace("=","")
	to_encrypt = set_2.pad(magic.encode('ascii'),16)
	return set_2.aes_cbc_mode_enc(to_encrypt, magic_key, magic_key)

#Note: I got stuck on this challenge because I was decrypting the bytes into ascii, which doesn't work 
#because the bit flipping attack results in a completely messed up block that can't be converted into ascii
def cbc_bad_decrypt(enc_bytes):
	text = set_2.aes_cbc_mode_dec(enc_bytes, magic_key, magic_key)
	#print(text)
	try:
		text.decode(encoding='ascii')
		print("text=",text)
	except UnicodeDecodeError:
		print("ascii error,returning ptxt")
		return text

def challenge_27():
	print('hi')
	x = cbc_bad_encrypt('A'*16 + 'A'*16 + 'A'*16)
	cbc_bad_decrypt(x)

	blocks = set_1.blockify(x,16)
	payload = blocks[0] + b'\x00' * 16 + blocks[0]

	res = cbc_bad_decrypt(payload)
	print(res)

	res_blocks = set_1.blockify(res,16)
	#blocks[2] is encrypted A's xor'd with 0, so just encrypted A's
	#blocks[0] is encrypted A's xor'd with the key, so we can recover the key

	key = set_1.fixed_xor(res_blocks[0],res_blocks[2])
	print("recovered key=",key)


	# try:
	# 	cbc_bad_decrypt(x)
	# except UnicodeDecodeError:
	# 	print('hi')


def sha1_auth_send(message,key):
	return sha1.sha1(key+message)

def make_sha1_padding(msg):

	msg_length = len(msg) * 8
	m = -(msg_length + 1 + 64) % 512

	# m+1 will always be a multiple of 8 in our case
	padded_msg = (msg + bytes([0b10000000]) + b'\x00'*(m//8) + msg_length.to_bytes(8, byteorder='big'))
	return padded_msg

key = urandom(1)*random.randint(5,100)
#key = urandom(16)

def break_fixed_prefix_sha():
	#The goal is to take a SHA hash and forge it to include a ;admin=true; token without losing the authenticity(the secret key in the front)

	original_message = "comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"
	original_bytes = bytes(original_message, encoding='ascii')
	print(original_bytes)

	mac_hex = sha1_auth_send(original_bytes,key)
	mac = codecs.decode(mac_hex,'hex')
	print("Original MAC", mac_hex,mac)

	for i in range(200):
		key_guess = i
		padded_msg = make_sha1_padding(bytes(urandom(key_guess))+original_bytes) #Create the padding that would have been created for our message
		padding = padded_msg[len(original_bytes)+key_guess:] #Steal the padding, this line and the above one isn't really necessary, but I use it to check my answer
		#print(padding)

		original_mac_length = len(original_bytes) + len(padding) + key_guess #This is what we guess is the original length of the message that went into the hash function
		#print(original_mac_length) #This should always be 128 or something like that, roof to the nearest 64 of the key+msg len

		#Grab the state
		state = [int.from_bytes(x, byteorder='big')
			for x in set_1.blockify(mac, 4)]

		extra = b";admin=true;"

		fake = fake_sha1.sha1(extra,state,original_mac_length)
		#print(fake)
		actual = sha1_auth_send(original_bytes+padding+extra, key)

		if fake == actual:
			print("Got it, key_len=",i,"Poisoned hash=",fake,"actual hash=",actual,'hash value=',original_bytes+padding+extra)

def md4_auth_send(message,key):
	return md4.MD4(key+message).finish()

def make_md4_padding(msg):

	msg_length = len(msg) * 8
	m = -(msg_length + 1 + 64) % 512

	# m+1 will always be a multiple of 8 in our case
	padded_msg = (msg + bytes([0b10000000]) + b'\x00'*(m//8) + msg_length.to_bytes(8, byteorder='little')) #this goddamn little endianess
	return padded_msg

def break_fixed_prefix_md4():
	#MD4's turn to get rekt

	original_message = "comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"
	original_bytes = bytes(original_message, encoding='ascii')
	print(original_bytes)

	mac = md4_auth_send(original_bytes,key)
	print("Original MAC", mac)

	for i in range(200):
		key_guess = i
		padded_msg = make_md4_padding(bytes(urandom(key_guess))+original_bytes) #NO, MD4 USES LITTLE ENDIAN REPRESENTATIONS, 
		padding = padded_msg[len(original_bytes)+key_guess:] #Steal the padding, this line and the above one isn't really necessary, but I use it to check my answer
		#print(padding)

		original_mac_length = len(original_bytes) + len(padding) + key_guess #This is what we guess is the original length of the message that went into the hash function
		#print(original_mac_length) #This should always be 128 or something like that, roof to the nearest 64 of the key+msg len

		#Grab the state
		state = [int.from_bytes(x, byteorder='little')
			for x in set_1.blockify(mac, 4)]
		#print(state)
		extra = b";admin=true;"

		count = int(original_mac_length/64) #Count coresponds with the number of chunks that have been proccessed
		fake = fake_md4.MD4(extra,state,count).finish()

		actual = md4_auth_send(original_bytes+padding+extra, key)
		#print(fake,actual)
		if fake == actual:
			print("Got it, key_len=",i,"Poisoned hash=",codecs.encode(fake,'hex'),"actual hash=",codecs.encode(actual,'hex'), 'hash value=',original_bytes+padding+extra)

def sha1_HMAC(message,key):
	block_size = 64
	output_size = 20

	if len(key) > block_size:
		key = codecs.decode(sha1.sha1(key),'hex')

	if len(key) < block_size:
		key = key + b'\x00' * (block_size - len(key))

	for_o = (64 * 0x5c).to_bytes(10,'big')
	for_i = (64 * 0x36).to_bytes(10,'big')

	if len(for_o) < block_size:
		for_o = (block_size - len(for_o)) * b'\x00' + for_o

	if len(for_i) < block_size:
		for_i = (block_size - len(for_i)) * b'\x00' + for_i

	o_key_pad = set_1.fixed_xor(key,for_o)
	i_key_pad = set_1.fixed_xor(key,for_i)

	return codecs.decode(sha1.sha1(o_key_pad + codecs.decode(sha1.sha1(i_key_pad + message),'hex')),'hex')

def send_test(file, signature):
	start = time.perf_counter()
	try:
		response = urllib.request.urlopen('http://localhost:9000/test?file=' + file + '&signature=' + signature.decode('ascii'))
		end = time.perf_counter()
		print("got em")

		return (True, end - start)
	except urllib.error.HTTPError as e:
		end = time.perf_counter()
		return (False, end - start) #returns the time taken and that we did not get the right signature

def challenge_31():
	print("uhh")
	file = "meow"
	#The idea is that we know we get a byte of the actual digest correct for every 50ms of delay we observe, so we test until we get observe a delay in the server
	current = b''
	guess = b'\x00'
	guess_int = 0
	cur_len = 0
	delay_time = 0.02
	while True:
		guess = bytes([guess_int])
		next_guess = binascii.hexlify(current+guess)
		next_guess = next_guess + b'0'*(40-len(next_guess))
		#print(len(next_guess))
		print("guess =",next_guess)
		res,time_taken = send_test(file,next_guess)
		if res:
			print("EZPZ")
			break
		if math.floor(time_taken/delay_time) > cur_len:
			print("found another byte")
			current+=guess
			guess =  b'\x00'
			guess_int = 0
			cur_len +=1
		else:
			guess_int+=1
			if guess_int >= 256:
				raise Exception("uh oh")
	print("valid HMAC=",(current+guess).decode('ascii'))

def challenge_32():
	print("uhh")
	file = "meow"
	#just make changes to make the attack more consistent
	current = b''
	guess = b'\x00'
	guess_int = 0
	cur_len = 0
	delay_time = 0.02
	possible = []
	while True:
		guess = bytes([guess_int])
		next_guess = binascii.hexlify(current+guess)
		if len(next_guess) > 40:
			raise Exception("uhoh")
		next_guess = next_guess + b'0'*(40-len(next_guess))
		#print(len(next_guess))
		print("guess =",next_guess)
		res,time_taken_1 = send_test(file,next_guess)
		res,time_taken_2 = send_test(file,next_guess)
		res,time_taken_3 = send_test(file,next_guess)

		if res:
			print("EZPZ")
			break

		avg_time_taken = (time_taken_1+time_taken_2+time_taken_3)/3

		guess_int+=1
		possible.append((guess,avg_time_taken)) #because the timing is alot more strict we just take whatever took the longest avg time
		if guess_int >= 256:
			#print(possible)
			sorted_possible = sorted(possible, key=lambda x: x[1], reverse=True)
			current+=sorted_possible[0][0]
			guess =  b'\x00'
			guess_int = 0
			cur_len +=1
			possible = []
	print("valid HMAC=",(current+guess))

#Challenge 25
# x = ctr_encrypt_me(open('25.txt'))
# #print(x)
# y = edit(x, the_key, 0, b'aaaa bbbb cccc why does this only work sometimes')
# #print(y)
# #print(set_3.aes_ctr_mode_dec(y, the_nonce, the_key))

# #in theory z should just be the entire keystream
# z = edit(x, the_key, 0, bytes([0]) * len(x))

# res = set_1.fixed_xor(x,z)
# print(b64decode(res))

#challenge 26
# x = ctr_magic_encrypt("hi ctr")
# y = ctr_magic_decrypt(x)
# print(y)
# challenge_26()

#challenge 27
#challenge_27()

#Challenge 28
#Credit: https://github.com/ajalt/python-sha1
# x = sha1_auth_send(b'my secret sauceee',b'AAAAAAA')
# print(x)
# print('BCD49D2C263364EB51534FC1D79FC754B04561FF') #from https://passwordsgenerator.net/sha1-hash-generator/
# y = codecs.decode(x,'hex')
# print(y)

#Challenge 29
#break_fixed_prefix_sha()

#Challenge 30
#break_fixed_prefix_md4()

#Challenge 31
# x = sha1_HMAC(b"meow",b'ICE ICE BABY')
# print(codecs.encode(x,'hex')) 
# http://localhost:9000/test?file=meow&signature=475e1430a1a11e7a47a6b383a2d43a3be6920e42
#challenge_31()

#Challenge 32
#challenge_32()