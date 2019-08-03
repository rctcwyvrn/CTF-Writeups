import rsa_utils as rsa
import dsa_utils as dsa
from Crypto.Util import number
import set_5
import binascii, hashlib, base64, math
from decimal import *

r = None
old = []

def oracle_enc(message):
	return r.enc(message)

def oracle_dec(blob):
	if blob not in old:
		old.append(blob)
		return r.dec(blob)
	else:
		print("Server: message already decrypted before")

def challenge41():
	c1 = oracle_enc("all your secrets belong to us")
	print("result of test decryption, should be all your secrets belong to us : ",oracle_dec(c1))
	print("making sure the server rejects duplicate decrpytions")
	oracle_dec(c1)
	e,n = r.pubkey()
	#print(e,n)

	s = 12

	new_ciphertext = ((s**e % n) * c1) % n # this = (s * message) ** (e) mod n

	m2 = oracle_dec(new_ciphertext) #so then this = s * message mod n
	#print(m2)

	recovered_ptxt = m2 * number.inverse(s,n) % n #oops!
	print("recovered ptxt = ",number.long_to_bytes(recovered_ptxt))

def rsa_verify_signature(sig,msg):
	res = r.enc(sig)
	blocks = b'\x00' + number.long_to_bytes(res)
	if len(blocks) % 16 != 0:
		print("message length incorrect")
		return False
	#print("before stripping",blocks)
	i = 0 
	next_must_be_zero = False
	for byte in blocks:
		if i == 0 and byte != 0:
			print("first byte not 00h", byte)
			return None

		if byte != 1 and i == 1:
			print("second byte not 01h")
			return None

		if byte != 255 and i > 1:
			if byte == 0:
				break
			else:
				print("did not end in 00h, instead byte=",byte)
				return False
		i+=1

	stuff = blocks[i+1:i+33]
	sha = hashlib.sha256()
	sha.update(msg)
	msg_hash = sha.digest()
	if stuff == msg_hash:
		print("Server: Signature accepted, message= {}".format(msg))
	else:
		print("Signature rejected. Recieved {} instead of {}".format(stuff, msg_hash))

def rsa_sign(msg):
	actual_pad = b'\x00'
	val = actual_pad + msg

	if len(val) % 16 != 15:
		actual_pad += b'\x01'
		val = actual_pad + msg

		while len(val) % 16 != 15:
			actual_pad += b'\xff'
			val = actual_pad + msg

		actual_pad += b'\x00'
		val = actual_pad + msg

	#print(len(val) % 16)
	assert(len(val) % 16 == 0)
	print("signature before dec",val)
	return r.dec(int.from_bytes(val, byteorder = "big"))

def forge_signature(message):
	space = 0
	len_diff = 9999
	buffer_size = 64
	while len_diff > space:
		print("buffer too small, increasing to ",buffer_size)
		s = hashlib.sha256()
		s.update(message)
		fake = b'\x00\x01\xff\x00' + s.digest()
		#fake = fake + (128-len(fake)) * b'\x00'
		space = buffer_size - len(fake)
		fake = fake + space * b'\x00'

		#fake = fake[:16]
		#print(fake, number.bytes_to_long(fake) < r.pubkey()[1]) #we see that its tiny compared to the modulus
		if not number.bytes_to_long(fake) < r.pubkey()[1]:
			print("need to change something, this one won't work")
			return None
		#print(number.bytes_to_long(fake))
		#print("cube root = ",set_5.cube_root(number.bytes_to_long(fake)))


		fake_sig = set_5.cube_root(number.bytes_to_long(fake))
		t = int(fake_sig)
		diff = t**3 - number.bytes_to_long(fake)
		#print("difference", diff)
		#print("space=",space)
		#print("diff in bytes = ", len(number.long_to_bytes(diff)))
		len_diff = len(number.long_to_bytes(diff))

		buffer_size+=16
	print("signature has been forged, will decrypt to = {}".format(number.long_to_bytes(fake_sig ** 3)))
	print("Diff = {}, Space = {}".format(len_diff,space))
	return int(fake_sig)

def challenge42():
	message = b"gosh darn it"
	sha = hashlib.sha256()
	sha.update(message)
	test_message = sha.digest()

	signed = rsa_sign(test_message) #int
	rsa_verify_signature(signed, message)

	message = b'who needs private keys anyway'
	fake_sig = forge_signature(message)
	rsa_verify_signature(fake_sig, message)

def extract_privkey(r,s,k,H,q):
	x = (number.inverse(r,q) * (s*k -H)) % q
	return x

def challenge43():
	msg = b'somebody once told me'
	d = dsa.dsa()
	H = d.H(msg)

	r,s,k = d.sign_oops(msg)
	#print(r,s,k)
	#print("extracted private key",extract_privkey(r,s,k,H,dsa.q))

# 	pub = """84ad4719d044495496a3201c8ff484feb45b962e7302e56a392aee4abab3e4bdebf2955b4736012f21a08084056b19bcd7fee56048e004e44984e2f411788efdc837a0d2e5abb7b555039fd243ac01f0fb2ed1dec568280ce678e931868d23eb095fde9d3779191b8c0299d6e07bbb283e6633451e535c45513b2d33c99ea17"""
	#msg = """For those that envy a MC it can be hazardous to your health
# So be friendly, a matter of life and death, just like a etch-a-sketch\n""".encode('ascii')
	r,s,k = d.sign_oops(msg)
	#print(r,s,k)
	#print("extracted private key",extract_privkey(r,s,k,H,dsa.q))
# 	print(msg)
# 	h = hashlib.sha1()
# 	h.update(msg)
# 	print("string hash",h.hexdigest())
	#d2d0714f014a9784047eaeccf956520045c45265
	#d2d0714f014a9784047eaeccf956520045c45265 yeet


	msgH = 0xd2d0714f014a9784047eaeccf956520045c45265
	r = 548099063082341131477253921760299949438196259240
	s = 857042759984254168557880549501802188789837994940
	goal = "0954edd5e0afe5542a4adf012611a91912a3ec16"
	y = int("84ad4719d044495496a3201c8ff484feb45b962e7302e56a392aee4"
      "abab3e4bdebf2955b4736012f21a08084056b19bcd7fee56048e004"
      "e44984e2f411788efdc837a0d2e5abb7b555039fd243ac01f0fb2ed"
      "1dec568280ce678e931868d23eb095fde9d3779191b8c0299d6e07b"
      "bb283e6633451e535c45513b2d33c99ea17",16)
	for k in range(2**16):
		x = extract_privkey(r,s,k,msgH,dsa.q)

		#test_bytes = number.long_to_bytes(x)
		test_bytes = hex(x)[2:].encode()
		h = hashlib.sha1()
		h.update(test_bytes)
		hex_out = h.hexdigest()

		# if len(hex_out) != len(goal):
		# 	print("not right")
		# 	break

		if pow(dsa.g,x,dsa.p) == y:
			print("private key x found, x= {}".format(x))
			if hex_out == goal:
				print("yay it works")
			else:
				print("why is converting ints to bytes the hardest part again...")
			break

def challenge44():
	f = open("44.txt")
	i = 0
	msgs = []
	ss = []
	rs = []
	ms = []
	for line in f.readlines():
		if i == 0:
			msgs.append(line[:-2])
		elif i == 1:
			ss.append(int(line[3:]))
		elif i == 2:
			rs.append(int(line[3:]))
		else:
			ms.append(int(line.strip()[3:],16))

		i+=1
		i = i % 4
	#print(msgs,ss,rs,ms)

	#see if there are any duplicate r's because that would mean duplicate k

	for i in range(len(rs)):
		for j in range(len(rs)):
			if i != j and rs[i] == rs[j]:
				print("duplicate i={}, j={}".format(i,j))
				found = True
				break
		if found:
			break

	# i = 2
	# j = 10 also works!
	m1 = ms[i]
	s1 = ss[i]

	m2 = ms[j]
	s2 = ss[j]

	k = (number.inverse((s1-s2)%dsa.q,dsa.q) * (m1-m2)) % dsa.q #yeet

	x = extract_privkey(rs[i],ss[i],k,ms[i],dsa.q)

	h = hashlib.sha1()
	h.update(hex(x)[2:].encode())
	assert(h.hexdigest() == "ca8f6f7c66fa362d40760d135b763eb8527d3d52")

	print("got em x = {}".format(x))

def challenge45():
	bad_dsa = dsa.dsa(p3 = dsa.p+1)
	r,s = bad_dsa.sign(b'hello there')
	print(r,s)
	bad_dsa.verify((r,s),b'hello there')
	y = bad_dsa.pubkey()
	print("whats ur pubkey? Making sure its 1. y= {}".format(y)) #this is 1, youll see if you do the binomial expansion of (p+1) ** x mod p. Every term has a p except the constant term, which is 1
	#Generate some magic signature

	r = 1 #turns out theyre both just 1 lol
	s = 1 #do the math and you'll see. z is arbitrary so z = 1 should work

	#r is obviously 1 if you trace the first part of sign
	#but I'm not sure why s is also always 1. If you follow their equations it makes sense, but I don't see if from sign()

	bad_dsa.verify((r,s),b'hello there')
	bad_dsa.verify((r,s),b'cya nerds')

def rsa_parity_oracle(blob):
	ptxt = r.dec(blob)

	if isinstance(ptxt,str):
		ptxt = ptxt.encode('utf-8')
		ptxt = number.bytes_to_long(ptxt)

	#ptxt is an int
	bits = "{0:b}".format(ptxt)
	return bits[-1] == "0"

def challenge46():
	c_odd = r.enc(111)
	print(rsa_parity_oracle(c_odd))

	c_even = r.enc(200)
	print(rsa_parity_oracle(c_even))

	goal = base64.b64decode("VGhhdCdzIHdoeSBJIGZvdW5kIHlvdSBkb24ndCBwbGF5IGFyb3VuZCB3aXRoIHRoZSBGdW5reSBDb2xkIE1lZGluYQ==")
	#goal = """Somebody once told me the world is gonna roll me I ain't the sharpest tool in the shed""".encode('ascii')
	#enc_goal = r.enc(int.from_bytes(goal,byteorder='big'))
	enc_goal = r.enc(number.bytes_to_long(goal)) # should just be a big int


	e,N = r.pubkey()

	upper_bound = Decimal(N)
	lower_bound = Decimal(0)

	enc_two = pow(2,e,N)
	count = int(math.ceil(math.log(N,2)))

	getcontext().prec = count+10 #we need exactly count many bits of precisiom, i just added some more for lulz

	for i in range(1,count):
		#test = enc_bits[i:]
		blob_test =  (enc_two ** i) * enc_goal #multiplies the ptxt by 2**i
		diff = Decimal(N)/(2 ** i)

		if rsa_parity_oracle(blob_test):
			#even, so plaintext didn't wrap the modulus

			#So ptxt is less than half of the modulus	
			upper_bound-=diff

		else:
			lower_bound+=diff

		# if lower_bound >= upper_bound:
		# 	print("loop_count =",i)
		# 	print("expected count =",count)
		# 	break

		print(number.long_to_bytes(upper_bound))
		# j = count - i
		# if j <= 86:
		# 	print("{} cycles left, current ptxt = {}".format(j,number.long_to_bytes(upper_bound)[:86-j]))
		# else:
		# 	print(number.long_to_bytes(upper_bound))
	#extend the original idea to higher powers, ie multiplying by 4
	#case 1, wraps 0 times, parity is even, upper bound = n/4
	#case 2, wraps 1 time, parity is odd, lower bound is n/4 and upper bound is n/2
	#case 3, wraps 2 times, parity is even, lower bound is n/2 and the upper bound is 3n/4
	#case 4, wraps 3 times, partiy is odd, lower bound is 3n/4

	#We can determine which case it is by looking at the earlier ones, since this is a BST.
	#Going left == parity is even, which decreases our upper bound by n/(2 ** i)
	#Going right == parity is odd, which increases our lower bound by n/(2 ** i)

	#Check for multiplying by 8. L = n/2, U = 3n/4 
	#after multiplying, L = 4n, U = 6n, so it either wrapped 5 times or 4 tims
	#if parity is even, then it wrapped an even number of times, so to less than 5 times, so the upper bound is decreased to 5n/8
	#if parity is odd, then it wrapped around an odd number of times, to at least 5 times, so the lower bound is increased to 5n/8

	#(L+U)/2 = (5/4)/2 = 5/8

	#print(lower_bound,upper_bound)
	#So at this point we're pretty sure the upper bound or lower bound is the plaintext
	t1 = number.long_to_bytes(lower_bound)
	t2 = number.long_to_bytes(upper_bound)

	print("Recovered ptxt = ",t1.decode('ascii'))



def challenges():
	global r
	r = rsa.rsa(3)


	#Challenge 41
	#challenge41()

	#Challenge 42
	#challenge42()

	#Challenge 43
	#challenge43()

	#Challenge 44
	#challenge44()

	#Challenge 45
	#challenge45()

	#Challenge 46
	challenge46()

if __name__ == "__main__":
	challenges()