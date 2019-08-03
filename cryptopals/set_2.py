from Crypto.Cipher import AES
import set_1
import codecs
import math
import os, random

class BadPaddingException(Exception):
	pass


def aes_block_dec(enc, key):
	enc = pad(enc,16)
	aes = AES.new(key, AES.MODE_ECB)
	return aes.decrypt(enc)

def aes_block_enc(plain_text, key):
	plain_text = pad(plain_text,16)
	aes = AES.new(key, AES.MODE_ECB)
	to_encrypt = pad(bytes(plain_text), 16)
	return aes.encrypt(to_encrypt)

def pad(in_bytes, pad_len):
	num_bytes = (pad_len - len(in_bytes)) % pad_len
	append = bytes([num_bytes])
	for i in range(num_bytes):
		in_bytes+=append
	return in_bytes

def aes_ecb_mode_enc(in_bytes, key):
	blocks = set_1.blockify(pad(in_bytes,16),16)
	out = b''
	for block in blocks:
		out+=aes_block_enc(block,key)
	return out

def aes_ecb_mode_dec(in_bytes, key):
	blocks = set_1.blockify(pad(in_bytes,16),16)
	out = b''
	for block in blocks:
		out+=aes_block_dec(block,key)
	return out

def base64_to_bytes(in_text):
	out = b''
	for char in in_text:
		out+=bytes([ord(char)])
	return out


def aes_cbc_mode_dec_file(file, IV, key):
	lines = file.read().strip()
	enc_bytes = codecs.decode(lines.encode(),'base64')
	return aes_cbc_mode_dec(enc_bytes, IV, key)

def aes_cbc_mode_dec(in_bytes, IV, key):
	blocks = set_1.blockify(in_bytes,16)
	out = b''
	for block in blocks:
		last = set_1.fixed_xor(aes_block_dec(block,key),IV)
		IV = block
		out +=last
	return out

def aes_cbc_mode_enc(in_bytes, IV, key):
	blocks = set_1.blockify(in_bytes,16)
	out = b''
	for block in blocks:
		last = aes_block_enc(set_1.fixed_xor(block,IV),key)
		IV = last
		out +=last
	return out

def random_aes_key():
	#return random16 bytes
	return os.urandom(16)


def encryption_oracle(plain_text):
	#generate random key
	key = random_aes_key()
	plain_bytes = plain_text.encode('ascii')
	front_buf_len = random.randint(5,10)
	back_buf_len = random.randint(5,10)

	to_encrypt = os.urandom(front_buf_len) + plain_bytes + os.urandom(back_buf_len)
	#print(to_encrypt)
	choice = random.randint(0,1)
	answer = ""
	if choice == 0:
		res = aes_ecb_mode_enc(to_encrypt, key)
		print("ECB encrypted")
		answer="ECB"
	else:
		res = aes_cbc_mode_enc(to_encrypt,random_aes_key(),key)
		print("CBC encrypted")
		answer="CBC"

	#print(res)
	return res,answer

def guess_cipher_mode(oracle_fn):
	random_encryption,answer = oracle_fn('A'*64)
	#input in a bunch of repeating bytes
	#use the oracle
	blocks = set_1.blockify(random_encryption,16)

	#print(blocks)

	unique_blocks = len(set(blocks))
	#print(len(blocks),unique_blocks)
	#if it's in ECB mode then the encrpyted bytes will have lots of repeats in it as well
	if unique_blocks < len(blocks):
		print("Guess ECB\n\n")
		assert(answer=="ECB")
	else:
		print("Guess CBC\n\n")
		assert(answer=="CBC")
	#use that to determine the cipher mode

the_key = os.urandom(16)

def ecb_encrypt_buffers(plain_text):
	special_sauce = "Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
	plain_bytes = plain_text.encode('ascii')
	plain_bytes = plain_bytes + codecs.decode(special_sauce.encode(),'base64')
	# front_buf_len = random.randint(5,10)
	# back_buf_len = random.randint(5,10)

	#to_encrypt = os.urandom(front_buf_len) + plain_bytes + os.urandom(back_buf_len)

	return aes_ecb_mode_enc(plain_bytes,the_key)

def byte_at_a_time_simple():
	# for i in range(160):
	# 	res = ecb_encrypt_buffers('A'*i)
		# print(len(res)) confirms the buffer size
		# blocks = set_1.blockify(res,16)

		# if len(blocks) > len(set(blocks)):
		# 	print("is_ecb") confirms is ecb
	# one_byte_short = ecb_encrypt_buffers('A'*14)[0:16]
	# values = {}
	# for i in range(126):
	# 	values[chr(i)] = set_1.blockify(ecb_encrypt_buffers("A"*14 + "R" + chr(i)),16)[0]

	# #print(values)
	# for key,value in values.items():
	# 	#print(len(value))
	# 	if value == one_byte_short:
	# 		print(key)
	final = ""
	for x in range(10):
		print(len(final))
		for i in range(1,17):
			input_string = 'A'*(16-i)
			result = ecb_encrypt_buffers(input_string)[16*(x):16*(x+1)]
			values = {}
			for i in range(126):
				values[chr(i)] = set_1.blockify(ecb_encrypt_buffers(input_string + final + chr(i)),16)[x]
				#print(len(input_string + final + chr(i)))
				#assert(len(input_string + final + chr(i)) % 16 == 0)

			for key,value in values.items():
				#print(len(value))
				if value == result:
					print(final)
					final+=key
	print(final)
	return final

uid = 1

def parse(user_string):
	data = {}
	parts = user_string.split("&")

	for part in parts:
		key,value = part.split("=")
		data[key]=value

	return data

def filter_out(user_email):
	return user_email.replace("&","").replace("=","")


def profile_for(user_email):
	global uid
	user_data = ""
	user_data+="email=" + filter_out(user_email) + "&"
	user_data+= "uid=" + str(uid)+ "&"
	uid +=1
	user_data+= "role=" + "user"

	return user_data

random_key = os.urandom(16)

def encrypt_profile(profile_string):
	encrypted = aes_ecb_mode_enc(profile_string.encode('ascii'),random_key)
	return encrypted

def decrypt_profile(encrypted_profile):
	return parse(codecs.decode(aes_ecb_mode_dec(encrypted_profile,random_key),'ascii'))

def create_account(email):
	return encrypt_profile(profile_for(email))

def challenge_13():
	#Goal is to create an account such that when passed into decrypt profile says that we're admin
	#print(decrypt_profile(create_account("howard,lin314@gmail.com")))

	#The attack will go something like create an account where the role is in the last block, and also make one with admin in the username
	#Pull out what admin gets encrypted to
	#replace the last block which used to be the word 'user' encrypted with the word 'admin' encrypted

	#Weird email
	#email=_&uid=1&role= takes up 18 bytes, so we want our email to be exactly 14 bytes long to push user onto its own block with 12 bytes of padding
	#weird = create_account("A"*14)
	weird = create_account("abcd@gmail.com") #made it fancy, anything with 14 chars is fine

	#print(set_1.blockify(profile_for("A"*14).encode('ascii'),16))

	blocks = set_1.blockify(weird,16) #we eventually want to replace the third block in here
	#email=aaaaaaaaaaa
	#aaa&uid=1&role=
	#user 0x12 0x12 ...

	#email=abdc@gmail.
	#com&uid=1&role=
	#user 0x12 0x12 ...

	print(blocks[2])

	#Note that we have to put admin in with it's padding beforehand and also make sure that it's in it's own block, since aes encrypts blocks, not individual bytes

	admin_string = "A" * 10 + codecs.decode(pad(b"admin",16),'ascii')
	bad = create_account(admin_string)

	#email=AAAAAAAAAA
	#admin 0x11 0x11 0x11....
	#uid whatever....

	encrypted_admin_word = set_1.blockify(bad,16)[1]


	blocks[2] = encrypted_admin_word

	fake_admin = b''
	for block in blocks:
		fake_admin+=block

	print(fake_admin)
	print(decrypt_profile(fake_admin))


another_key = os.urandom(16)
prefix_length = random.randint(5,10)
the_prefix =  os.urandom(prefix_length)

#Random prefix length of random bytes, but is constant between runs
def ecb_encrypt_harder(plain_text):
	special_sauce = "Somebody once told me the world is gonna roll me, I aint the sharpest tool in the shed"
	plain_bytes = plain_text.encode('ascii')
	plain_bytes = the_prefix + plain_bytes + special_sauce.encode('ascii')
	#print("hint:",prefix_length)
	

	return aes_ecb_mode_enc(plain_bytes, another_key)

#A constantly changing prefix length and value
def ecb_encrypt_even_harder(plain_text):
	special_sauce = "She was lookin kinda dumb with a finger and a thumb in the shape, of an L, on her forehead. Well, the years start coming and the don't stop coming"
	plain_bytes = plain_text.encode('ascii')
	plain_bytes = os.urandom(random.randint(5,10)) + plain_bytes + special_sauce.encode('ascii')
	

	return aes_ecb_mode_enc(plain_bytes, another_key)



def one_byte_at_a_time_harder():

	#detect prefix length
	#we know it's constant so we can just send repeating info to determine it
	#The goal is to find how many A's we have to send until the first block is the same as the last, so we know exactly how long the prefix is
	#Note that this requires that the prefix be of constant value and length

	#how to do it for the even_harder one? I have n o i d e a, but only this part of the function needs to change
	prefix_length = 0
	last = set_1.blockify(ecb_encrypt_harder(""),16)[0]
	for i in range(1,30):
		test = set_1.blockify(ecb_encrypt_harder("A"*i),16)[0]
		if last == test:
			prefix_length = 16 - i + 1
			break
		else:
			last = test

	final = ""
	#first block is a bit different to account for the prefix
	for i in range(1,17-prefix_length):
		input_string = 'A'*(16 - prefix_length -i)
		result = ecb_encrypt_harder(input_string)[0:16]
		values = {}
		for i in range(126):
			values[chr(i)] = set_1.blockify(ecb_encrypt_harder(input_string+ final + chr(i)),16)[0]
			#print(len(input_string + final + chr(i)))
			#assert(len(input_string + final + chr(i)) % 16 == 0)

		for key,value in values.items():
			#print(len(value))
			if value == result:
				print(final)
				final+=key

	#rest of the blocks are same as normal
	for x in range(1,7):
		print(len(final))
		for i in range(1,17):
			input_string = 'A'*(16 -i)
			result = ecb_encrypt_harder(input_string)[16*(x):16*(x+1)]
			values = {}
			for i in range(126):
				values[chr(i)] = set_1.blockify(ecb_encrypt_harder(input_string+ final + chr(i)),16)[x]
				#print(len(input_string + final + chr(i)))
				#assert(len(input_string + final + chr(i)) % 16 == 0)

			for key,value in values.items():
				#print(len(value))
				if value == result:
					print(final)
					final+=key
	print(final)
	return final
	

def verify_and_strip(padded_bytes):
	if len(padded_bytes) % 16 != 0:
		raise BadPaddingException()

	#find what the padding byte is
	#padding_byte = 16
	#padding_int = 16
	padding_int = 0
	padding_byte = 0
	for i in range(17):
		test = bytes([i])
		if padded_bytes[len(padded_bytes)-1] == i:
			padding_int = i
			padding_byte = test
			break

	#print("Padding byte is (hopefully):",padding_byte)
	
	#strip
	fixed_bytes = b''
	start = 0
	for i in range(len(padded_bytes)):
		j = len(padded_bytes) - i - 1
		if(padded_bytes[j] != padding_int):
			start = j
			break
	#print("change:",start)
	for i in range(start+1):
		fixed_bytes+=bytes([padded_bytes[i]])

	#print("stripped:",fixed_bytes)

	if  16 - (len(fixed_bytes) % 16 ) != padding_int:
		raise BadPaddingException()
	else:
		#print("padding verified, its good")
		return fixed_bytes


magic_key = os.urandom(16)
magic_IV = os.urandom(16)

def cbc_magic_encrypt(plain_text):
	magic = "comment1=cooking%20MCs;userdata=" + plain_text.replace(";","").replace("=","") + ";comment2=%20like%20a%20pound%20of%20bacon"
	to_encrypt = pad(magic.encode('ascii'),16)
	return aes_cbc_mode_enc(to_encrypt, magic_IV, magic_key)

#Note: I got stuck on this challenge because I was decrypting the bytes into ascii, which doesn't work 
#because the bit flipping attack results in a completely messed up block that can't be converted into ascii
def cbc_magic_decrypt(enc_bytes):
	text = aes_cbc_mode_dec(enc_bytes,magic_IV, magic_key)
	print(text)
	if b';admin=true;' in text:
		print("admin access granted!")
		return True
	return False

def challenge_16():
	#print(len(b';admin=true'))
	magic_sauce = set_1.fixed_xor(b';admin=true;', b'AAAAAAAAAAAA')
	#print(magic_sauce)

	#print(len(b"comment1=cooking%20MCs;userdata="))

	to_flip = cbc_magic_encrypt('A'*16)
	print(len(to_flip))
	print(to_flip)
	payload = b''

	blocks = set_1.blockify(to_flip,16)

	#the previous ciphertext block A gets xor'd against something x to get "AAAAA..."
	#So replace A with A xor ";admin=true;" xor "AAAAA..."
	#So x xor payload_block = "AAAAA..." xor "AAAA...." xor ';admin=true;'
	#so it results in the plaintext ;admin=true;

	payload += blocks[0]
	payload += set_1.fixed_xor(blocks[1], magic_sauce + b'\x00' * 4)
	for i in range(2,len(blocks)):
		payload += blocks[i] 

	print(len(payload))

	print(payload)
	res = cbc_magic_decrypt(payload)

	#Moral of challenge 13 and 16, things aren't safe if attackers have access to your ciphertext since they can change the message to be whatever they want
	#But the contents of the message are still safe


#challenge 10 
# IV = bytes([0x00]*16)
# a = aes_cbc_mode_dec_file(open('10.txt'),IV,b'YELLOW SUBMARINE')
# print(a.decode('ascii'))

#challenge 11
# encryption_oracle("meoww")
# for i in range(200):
# 	guess_cipher_mode(encryption_oracle)

#challenge 12
#byte_at_a_time_simple()


#challenge 13
# x = profile_for("howard.lin@gmail.com")
# y = encrypt_profile(x)
# z = decrypt_profile(y)

# print(x)
# print(y)
# print(z)

#print(create_account("howard,lin314@gmail.com"))
#vechallenge_13()

#challenge 14
#one_byte_at_a_time_harder()

#challenge 15
# test = pad("meowwwww".encode('ascii'),16)
# print(test)
# print(verify_and_strip(test))

# try:
# 	test2 = "meowwww".encode('ascii') + b'\x05'*9
# 	print(verify_and_strip(test2))
# 	print("exception not raised?")
# except BadPaddingException:
# 	print("bad padding exception! it works!")

# print(verify_and_strip(b"ICE ICE BABY\x04\x04\x04\x04"))

#challenge 16
#x = cbc_magic_encrypt("meowwwww")
#print(x)
#y = cbc_magic_decrypt(x)
#print(y)
#challenge_16()
