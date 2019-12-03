import rsa_utils as rsa
import dsa_utils as dsa
from Crypto.Util import number
import set_5
import binascii, hashlib, base64, math, os, random
from decimal import *

import multiprocessing, sys

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
# 	goal = """Somebody once told me the world is gonna roll me
# I ain't the sharpest tool in the shed
# She was looking kind of dumb with her finger and her thumb
# In the shape of an "L" on her forehead""".encode('ascii')
	#enc_goal = r.enc(int.from_bytes(goal,byteorder='big'))
	enc_goal = r.enc(number.bytes_to_long(goal)) # should just be a big int


	e,N = r.pubkey()

	upper_bound = Decimal(N)
	lower_bound = Decimal(0)

	enc_two = pow(2,e,N)
	count = int(math.ceil(math.log(N,2)))

	diff = N

	getcontext().prec = count+10 #we need exactly count many bits of precisiom, i just added some more for lulz

	for i in range(1,count):
		#test = enc_bits[i:]
		blob_test =  (enc_two ** i) * enc_goal #multiplies the ptxt by 2**i
		#diff = Decimal(N)/(2 ** i)
		diff = diff//2

		if rsa_parity_oracle(blob_test):
			#even, so plaintext didn't wrap the modulus

			#So ptxt is less than half of the modulus	
			print("yes")
			upper_bound-=diff

		else:
			print("no")
			lower_bound+=diff

		# if lower_bound >= upper_bound:
		# 	print("loop_count =",i)
		# 	print("expected count =",count)
		# 	break

		#print("loop # {} out of {}: ".format(i,count),number.long_to_bytes(upper_bound))
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

class MessageTooLong(Exception):
	pass

#total_server_requests = 0
server_lock = multiprocessing.Lock()

def rsa_pad_enc(data):
	k = len(number.long_to_bytes(r.pubkey()[1]))

	if k - 3 - len(data) < 8:
		print("message too long")
		raise MessageTooLong

	pad_str = os.urandom(k - 3 - len(data)) #pads the message up to the bytelen of the modulus, so the msg is exactly 1 modulus long
	res =  b'\x00\x02' + pad_str + b'\x00' + data
	x = number.bytes_to_long(res)
	print(res,x)
	print(len(res))
	return r.enc(x), res

#import time

def rsa_padding_oracle(blob, counter):
	x = r.dec(blob)
	length = len(number.long_to_bytes(r.pubkey()[1]))
	res = number.long_to_bytes(x,length)

	global server_lock
	server_lock.acquire()
	counter.value += 1
	#print("--- LOCKED total server requests = ", counter.value)
	#time.sleep(0.5)
	#print("--- server releasing lock")
	server_lock.release()

	return res[0] == 0 and res[1] == 2

def multithread(q, lock , counter, c, e, n, conn):
	print("Starting thread")
	global to_test 
	attempts = 0
	while True:
		

		lock.acquire()
		if q.empty():
			print("--- adding new items")
			for i in range(s, s + 10**4):
				q.put(i)
			print("Total requests made so far: ", counter.value)
			print("--- done")
		lock.release()

		s = q.get()
		#print("Testing s=",s)

		attempts+=1
		c_test = (c * pow(s,e,n)) % n
		#print(c_test)
		#print(to_test.qsize())
		if attempts % 500 == 0:
			print("this thread has made {} attempts".format(attempts))

		if rsa_padding_oracle(c_test, counter):
			lock.acquire()
			print("Solution found! Clearing queue")

			while not q.empty():
				q.get()

			q.put(s)
			q.put(s)
			q.put(s)
			q.put(s)
			q.put(s)
			q.put(s)
			q.put(s)
			q.put(s)

			conn.send(s)
			conn.close()

			print("found s = {}, exiting thread".format(s))
			lock.release()
			return
		#else:
			#to_test.put(s+8)

def threaded_find_s(c, e, n, B, total_requests, start_val):
	threads = []

	print("preparing queue")
	to_test = multiprocessing.Queue()
	lock = multiprocessing.Lock()
	for i in range(start_val, start_val + 10**4):
		to_test.put(i)

	parent_pipes = []
	for i in range(1,9):
		p_c, c_c = multiprocessing.Pipe()
		parent_pipes.append(p_c)
		t = multiprocessing.Process(target=multithread,args=[to_test, lock, total_requests, c,e,n,c_c])
		t.start()
		threads.append(t)

	print("Created threads")
	vals = []

	for p_c in parent_pipes:
		vals.append(p_c.recv())
	print("joining threads")
	for t in threads:
		t.join()


	assert(len(list(set(vals))) == 1)
	s_1 = vals[0]
	print("returned, and we found s=",s_1)
	assert(rsa_padding_oracle((c*pow(s_1,e,n))%n, total_requests))

	return s_1

def ceil(a,b):
	return (a+b-1) // b

def narrow_solutions(M, s, B, n):
	new_M = []
	for (a,b) in M:
		#print(a,b,s,B)
		#print("new r range",math.ceil((a*s-3*B+1)/n), (b*s-2*B)//n + 1)
		for r in range(ceil((a*s-3*B+1),n), (b*s-2*B)//n + 1):
			#print("makingnew range from r = ",r)
			new_a = ceil((2*B+r*n),s)

			#new_b = math.floor((3*B-1+r*n)/s) #apparantely this one is less accurate
			new_b = (3*B-1+r*n)//s

			# if new_b_1 != new_b_2:
			# 	print("waht the fuck")
			# 	print(new_b_2 - new_b_1)
			# 	print(new_b_1, new_b_2)
			# 	sys.exit(1)

			# else:
			# 	new_b = new_b_1

			new_M_pair = [0,0]

			if new_a > a:
				new_M_pair[0] = new_a 
			else:
				new_M_pair[0] = a

			if new_b < b:
				new_M_pair[1] = new_b
			else:
				new_M_pair[1] = b 

			unique = True
			for a_in,b_in in new_M:
				if new_M_pair[0] == a_in and new_M_pair[1] == b_in:
					unique = False
					break

			if unique:
				new_M.append(new_M_pair)

	#print("new M =",new_M)
	print("Contains {} interval(s)".format(len(new_M)))
	return new_M


def rsa_pad_oracle_attack(c,rsa, multi=True):
	total_requests = multiprocessing.Value("i",0)
	e,n = rsa.pubkey()
	k = len(number.long_to_bytes(n))

	B = 2 ** (8 *(k-2)) #PKCS conformance of c' = c* s**(e) mod n implies 2B <= ms mod n <= 3B
	#print(c)
	#step 1: find a first s0

	# for s in range(2,10**5):
	# 	c_test = (c * (s**e) ) % n 
	# 	#print("ctest:",s)
	# 	if rsa_padding_oracle(c_test):
	# 		print("found one!")
	# 		c_0 = c_test
	# 		M_0 = (2*B, 3*B-1)
	# 		i = 1
	# 		break

	#We can ignore step 1 because c is already pkcs conforming

	s = [1]
	M = [(2*B, 3*B-1)]
	i = 1

	if not multi:
		#print(c_0,M_0,i)
		print("--- 2a")
		found = False
		for s_1 in range(ceil(n,(3*B)), n):
			#print(s_1)
			c_test = (c * pow(s_1,e,n) ) % n 
			if rsa_padding_oracle(c_test, total_requests):
				found = True
				break
			if total_requests % 1000 == 0:
				print("attempts in this 2a =",total_requests.value)

		if found:
			s.append(s_1)
			print("new s_i=",s_1)
		else:
			print("fak")
			sys.exit(1)
	else:
		print("--- mulithreaded 2a")
		s_1 = threaded_find_s(c, e, n, B, total_requests, ceil(n,3*B))
		s.append(s_1)

	last_diff = M[0][1] - M[0][0]

	#Step 3
	print("narrowing solutions for i=1")
	M = narrow_solutions(M, s_1, B, n)

	count = 0

	print("Entering search loop")
	while(count <= 10**6):
		print("# of iterations so far = ",count)
		print("# of requests made to server = ",total_requests.value)
		#Step 2b and 2c
		if len(M) > 1:

			if not multi:
				found = False
				print("--- 2b")
				attempts = 0
				#print(s,s[-1])
				for s_i in range(s[-1]+1, n):

					c_test = (c * pow(s_i,e,n) ) % n 
					attempts+=1

					if attempts % 1000 == 0:
						print("{} attempts in this 2b".format(attempts))

					if rsa_padding_oracle(c_test, total_requests):
						found = True
						break

				if found:
					print("Found new s_i=", s_i)
					s.append(s_i)
				else:
					print("fak")
					sys.exit(1)
			else:
				print("--- multithreaded 2b")
				s_i = threaded_find_s(c, e, n, B, total_requests, s[-1]+1)
				s.append(s_i)
		else:
			found = False
			print("--- 2c")
			a,b = M[0]
			relative = (b-a)/last_diff

			print("interval diff relative to last = {}".format(relative))
			#print("diff = ",b-a)
			print("log diff = ",math.log(b-a))

			if relative > 1 or b < a:
				print("fak")
				sys.exit(1)

			last_diff = b-a
			attempts = 0


			r = ceil(2*(b*s[-1] - 2*B),n)
			s_i = ceil((2*B + r*n),b)

			while True:

				c_test = (c* pow(s_i,e,n)) % n 
				attempts+=1

				if attempts % 50000 == 0:
					print("Attempts in this 2c = ",attempts)

				if rsa_padding_oracle(c_test, total_requests):
					found = True
					break

				if(s_i > (3*B+r*n)//a):
					r+=1
					s_i = ceil((2*B + r*n),b)
					#print("new r")
				else:
					s_i +=1

			print("total attempts=",attempts)
			if found:
				#print("Found new s_i=", s_i)
				s.append(s_i)
				if s_i < 0:
					print("fak bad solution")
					sys.exit(1)
			else:
				print("fak")
				sys.exit(1)

		#Step 3
		print("--- 3")
		print("narrowing solutions")
		M = narrow_solutions(M, s_i, B, n)

		if len(M) == 1 and (M[0][1] - M[0][0] == 0):
			#print(M)
			break

		count+=1

	print("Done!")
	global total_server_requests
	print("Total # of requests to server = ", total_requests.value)
	print(b'\x00'+number.long_to_bytes(M[0][0]))
	return b'\x00'+number.long_to_bytes(M[0][0])


def challenge47():
	global r 
	r = rsa.rsa(11, True)

	try:
		x,m = rsa_pad_enc(b"kick it, CC")
	except MessageTooLong:
		print(":c")
		return

	#print("oracle says",rsa_padding_oracle(x))
	#print("oracle says",rsa_padding_oracle(2))

	rsa_pad_oracle_attack(x,r,True)
	print(m)

def challenge48():
	#same code, since I implemented the full algorithm in challenge 47
	global r 
	r = rsa.rsa(11, False)

	try:
		x,m = rsa_pad_enc(b"kick it, CC")
	except MessageTooLong:
		print(":c")
		return

	#print("oracle says",rsa_padding_oracle(x))
	#print("oracle says",rsa_padding_oracle(2))

	result = rsa_pad_oracle_attack(x,r,True)
	print(m)
	print("Are they equal? ", result == m)

def challenges():
	global r
	r = rsa.rsa(65537)


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
	#challenge46()

	#Challenge 47
	#challenge47()

	#Challenge 48
	challenge48()

if __name__ == "__main__":
	challenges()