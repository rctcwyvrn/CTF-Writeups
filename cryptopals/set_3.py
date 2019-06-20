import set_1,set_2
import random
import os
import codecs, time
from base64 import b64decode

class fake_Twister:
	def __init__(self,state_array):
		self._index = 0
		self._MT = state_array

	def extract(self):
		return Twister.extract(self)

	def twist(self):
		return Twister.twist(self)

class Twister:
	def __init__(self, seed):
		self._index = 0
		self._MT = [0] * 624
		self._MT[0] = seed & 0xffffffff
		for i in range(1, 624):
			#Magic to get the state array started
			self._MT[i] = ((0x6c078965 * (self._MT[i-1] ^ (self._MT[i-1] >> 30))) + i) & 0xffffffff

	def extract(self):
		if self._index == 0:
			self.twist() #Gets called to start the state array

		#Tempering function
		y = self._MT[self._index]
		y ^= (y >> 11)
		y ^= ((y << 7) & 0x9d2c5680)
		y ^= ((y << 15) & 0xefc60000)
		y ^= (y >> 18)

		self._index = (self._index + 1) % 624
		return y #& 0xffff

	#Mix up the state array
	def twist(self):
		for i in range(624):
			#Magic that diffuses the seed into the state array
			y = (self._MT[i] & 0x80000000) + (self._MT[(i+1) % 624] & 0x7fffffff)
			self._MT[i] = self._MT[(i + 397) % 624] ^ (y >> 1)
			if y % 2 != 0:
				self._MT[i] ^= 0x9908b0df

def untemper_MT(r):

	def int_to_bit_list(x):
		return [int(b) for b in '{:032b}'.format(x)]

	def bit_list_to_int(l):
		return int(''.join(str(x) for x in l), base=2)

	def undo_shl(y,n,shift):
		y = int_to_bit_list(y)
		y.reverse()
		n = int_to_bit_list(n)
		n.reverse()
		x = []
		count = 0
		for i in range(len(y)):
			if i < shift:
				x.append(y[i])
			else:
				x.append(y[i] ^ (x[i-shift] & n[i]))

		x.reverse()
		return bit_list_to_int(x)

	def undo_shr(y,n,shift):
		y = int_to_bit_list(y)
		n = int_to_bit_list(n)
		x = []
		count = 0
		for i in range(len(y)):
			if i < shift:
				x.append(y[i])
			else:
				x.append(y[i] ^ (x[i-shift] & n[i]))
		return bit_list_to_int(x)

	r = undo_shr(r,0xffffffff,18)
	#print("one:",r)
	r = undo_shl(r,0xefc60000,15)
	#print("two:",r)
	r = undo_shl(r,0x9d2c5680,7)	
	#print("three:",r)
	r = undo_shr(r,0xffffffff,11)
	#print("four:",r)

	return r


my_key = os.urandom(16)
def get_secret():
	secrets = ["MDAwMDAwTm93IHRoYXQgdGhlIHBhcnR5IGlzIGp1bXBpbmc=",
	"MDAwMDAxV2l0aCB0aGUgYmFzcyBraWNrZWQgaW4gYW5kIHRoZSBWZWdhJ3MgYXJlIHB1bXBpbic=",
	"MDAwMDAyUXVpY2sgdG8gdGhlIHBvaW50LCB0byB0aGUgcG9pbnQsIG5vIGZha2luZw==",
	"MDAwMDAzQ29va2luZyBNQydzIGxpa2UgYSBwb3VuZCBvZiBiYWNvbg==",
	"MDAwMDA0QnVybmluZyAnZW0sIGlmIHlvdSBhaW4ndCBxdWljayBhbmQgbmltYmxl",
	"MDAwMDA1SSBnbyBjcmF6eSB3aGVuIEkgaGVhciBhIGN5bWJhbA==",
	"MDAwMDA2QW5kIGEgaGlnaCBoYXQgd2l0aCBhIHNvdXBlZCB1cCB0ZW1wbw==",
	"MDAwMDA3SSdtIG9uIGEgcm9sbCwgaXQncyB0aW1lIHRvIGdvIHNvbG8=",
	"MDAwMDA4b2xsaW4nIGluIG15IGZpdmUgcG9pbnQgb2g=",
	"MDAwMDA5aXRoIG15IHJhZy10b3AgZG93biBzbyBteSBoYWlyIGNhbiBibG93"]

	#secrets = ["A"*43, "DankMeems"*10]

	chosen = secrets[random.randint(0,9)]
	IV = os.urandom(16)
	print("secret = ",chosen.encode('ascii'))
	enc = set_2.aes_cbc_mode_enc(set_2.pad(chosen.encode('ascii'),16), IV, my_key)
	return enc, IV

def check_secret(enc_bytes, IV):
	res = set_2.aes_cbc_mode_dec(enc_bytes,IV,my_key)
	blocks = set_1.blockify(res,16)
	#print(blocks[-1])
	try: 
		a = set_2.verify_and_strip(res)
		return True
	except set_2.BadPaddingException:
		#print("fail:",res)
		return False

def padding_oracle_attack():

	# we know that if we change the last byte to be \0x01 then the padding oracle will say that the padding is valid
	# So we test random last bytes, modified ciphertext C', until C' xor Intermediate state = something something \0x01
	# Once we get there we can get the intermediate state, and since we have the cipher we can then get the plaintext as well
	cipher_text, IV = get_secret()
	blocks = set_1.blockify(cipher_text,16)
	m = len(blocks)
	inter = []
	for y in range(len(blocks)-1):

		base = b''
		for x in range(m-y-2): #m-y later
			base += blocks[x]

		for n in range(16):
			#print("Loop: n=",n, "y= ",y)
			extra = generate(inter,n,y)
			#if n>=1:
				#print("n=",n,"extra len=",len(extra), "extra = ",extra, "extra first byte=", extra[0], "inter", inter)
			answer = None
			for i in range(256):
				test = bytes([i])
				payload = base
				payload += b'A' * (15-n) + test + extra
				payload += blocks[m-y-1]
				#print(len(payload) + 16*y, " vs ", len(cipher_text))
				assert(len(payload) + 16*y == len(cipher_text))
				res = check_secret(payload, IV)
				if res:
					#print("found it:",i, "n=",n)
					answer = i
					break
			if answer == None:
				raise Exception("No answer found")
			#print("inter = ",(answer ^ (n+1)))
			inter = [(answer ^ (n+1))] + inter

		#print("next block")

	#now to get the first block we need to mess with the IV
	for n in range(16):
		#print("Loop: n=",n, "y= ",y)
		extra = generate(inter,n,y)
		#if n>=1:
			#print("n=",n,"extra len=",len(extra), "extra = ",extra, "inter", inter)
		answer = None
		for i in range(256):
			test = bytes([i])
			payload = b'A' * (15-n) + test + extra
			#print(len(payload) + 16*y, " vs ", len(cipher_text))
			assert(len(payload) == 16)
			payload += blocks[0]
			res = check_secret(payload,IV)
			if res:
				#print("found it:",i, "n=",n)
				answer = i
				break
		if answer == None:
			raise Exception("No answer found")
		#print("inter = ",(answer ^ (n+1)))
		inter = [(answer ^ (n+1))] + inter

	inter_bytes = bytes(inter)
	final = set_1.fixed_xor(inter_bytes, IV+cipher_text)
	print("final attack result = ",final)
	secret = codecs.decode(final,'ascii')
	print("GOT DEM SECRETS,",b64decode(secret))

def generate(inter_ints, m, block_number):
	ret = b''
	for i in range(m):
		ret += bytes([inter_ints[i] ^ (m+1)])
	return ret

def i2b(x):
	return x.to_bytes(8, byteorder="little")

def aes_ctr_mode_enc(plaintext, nonce, key):
	nonce = i2b(nonce)
	keystream = bytes()
	block_count = 0
	while len(keystream) < len(plaintext):
	    block = nonce + i2b(block_count)
	    #print(block)
	    keystream += set_2.aes_block_enc(block, key)
	    block_count += 1
	return set_1.fixed_xor(plaintext, keystream)

def aes_ctr_mode_dec(ciphertext, nonce, key):
	return aes_ctr_mode_enc(ciphertext,nonce,key)

def challenge_19():
	ciphertexts = []
	a_key = os.urandom(16)
	expected = b''

	f = open("19.txt","r")
	for line in f:
		to_enc = b64decode(line)
		expected+=to_enc
		ciphertexts.append(aes_ctr_mode_enc(to_enc,0,a_key))
	print("expected:",expected)
	#now to break the ciphertexts
	#We know the the first byte of all those ciphertexts = first_plaintext xor aes(lots of 0's), the important part is that it's the same, so we can just try every single one
	inter = b''
	for n in range(64):
		#n represents the index of the byte we're trying to attack
		scores = []
		for i in range(256):
			#i is the guess
			res_bytes = b''
			for ctxt in ciphertexts:
				if(len(ctxt) <= n):
					pass
				else:
					#Get the result of the guess on each ciphertext[n], the result being the plaintext we get from xoring
					res_bytes+=bytes([ctxt[n] ^ i])
			#get the score for that guess and append it		
			score = set_1.get_score(res_bytes)
			scores.append((score,i))

		#sort the guesses and take the best one
		sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)
		inter+=bytes([(sorted_scores[0][1])])

	#take all of our best guesses and get our plaintext 
	plain = b''
	for ctxt in ciphertexts:
		plain += set_1.fixed_xor(ctxt,inter)

	print("result:",plain)


def time_seed():
	print("starting wait")
	time.sleep(random.randint(40,100))
	time_stamp = int(time.time())
	print("getting timestamp and waiting, seed =",time_stamp)
	test = Twister(time_stamp)
	time.sleep(random.randint(40,100))
	print("getting rng")
	return test.extract()

def clone_MT(orig):
	# "The fake is of far greater value. In its deliberate attempt to be real, it's more real than the real thing." -Kaiki
	fake_MT = [0] * 624 
	for i in range(624):
		tap = orig.extract()
		fake_MT[i]= untemper_MT(tap)
	return fake_Twister(fake_MT)


def MT_stream_cipher(to_enc, key):
	key = key & 0xffff
	stream = Twister(key)
	res = b''
	for byte in to_enc:
		res += bytes([(stream.extract() & 0xff) ^ byte])
	return res

def MT_stream_enc(plaintext,key):
	to_enc = os.urandom(random.randint(5,10)) + plaintext.encode('ascii')
	return MT_stream_cipher(to_enc,key)
def MT_stream_dec(enc, key):
	return MT_stream_cipher(enc,key)


def MT_stream_brute_force(ciphertext):
	print("brute forcing time")
	scores = []
	for i in range(2 ** 12):
		res = MT_stream_cipher(ciphertext,i)
		score = set_1.get_score(res)
		scores.append((i,score))

	sorted_scores = sorted(scores, key = lambda x: x[1], reverse=True)
	return sorted_scores[0][0]

def create_token():
	t = Twister(int(time.time()) & 0xffff)
	res = bytes(t.extract() & 0xff for _ in range(16))
	return res

def is_token_MT_time_seeded(token):
	cur_time = int(time.time()) & 0xffff
	for i in range(2 ** 16):
		t = Twister(i)
		test = bytes(t.extract() & 0xff for _ in range(16))
		if test == token:
			print("key=",i)
			break

	print("current time:",cur_time, "brute forced seed:", i)
	if abs(cur_time-i) < 10:
		return True
	else: 
		return False	

#Challenge 17
# enc, IV = get_secret()
# print(check_secret(enc,IV))
#padding_oracle_attack()

#Challenge 18
# x = aes_ctr_mode_enc(b'A'*32 + b'B'*32 , 0, b'YELLOW SUBMARINE')
# print(aes_ctr_mode_dec(x,0,b'YELLOW SUBMARINE'))

# y = b64decode('L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ==')
# z = aes_ctr_mode_dec(y,0,b'YELLOW SUBMARINE')
# print(z)

#Challenge 19/20
#challenge_19()

#Challenge 21
# t = Twister(12412)

# for i in range(10):
# 	print(i,t.extract())

# u = Twister(55555)

# for i in range(10):
# 	print(i,u.extract())

#Challenge 22
# res = time_seed()

# for i in range(250):
# 	test = int(time.time())-i
# 	x = Twister(test).extract()
# 	if res == x:
# 		print("seed = ",test)
# 		seed = test
# print(seed)

#Challenge 23
# y = 42124
# print("0:",y)
# y ^= (y >> 11)
# print("1:",y)
# y ^= ((y << 7) & 0x9d2c5680)
# print("2:",y)
# y ^= ((y << 15) & 0xefc60000)
# print("3:",y)
# y ^= (y >> 18)
# print("4:",y)

# untemper_MT(y)
# t = Twister(24190)
# c = clone_MT(t)

# for i in range(10):
# 	print(t.extract(),c.extract())

#Challenge 24
# test_key = 421
# x = MT_stream_enc("Somebody once told me the world is gonna roll me",test_key)
# print(x)
# y = MT_stream_dec(x,test_key)
# print(y)
# z = MT_stream_brute_force(x)
# print("key = ",z)
# print(MT_stream_dec(x,z))
# token = create_token()
# print(token)
# print(is_token_MT_time_seeded(token))