import random, hashlib, socket, sock_util
from os import urandom
import set_1,set_2, sha1, time

big_p = "ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff"
big_p = int(big_p,16)

def mod_exp(base,power,modulus):
	return pow(base,power,modulus) #lol i was expecting to actually have to implement that

def diffie_hellman():
	p = big_p
	g = 2
	a = random.randint(0,p) % p
	A = mod_exp(g,a,p)#(g**a) % p
	b = random.randint(0,p) % p
	B = mod_exp(g,b,p)#(g**b) % p

	s = mod_exp(B,a,p)#(B**a) % p
	other_s = mod_exp(A,b,p)#(A**b) % p
	assert(s == other_s)
	return s


server_s = 0
def diffie_server(p,g,A):
	b = random.randint(0,p) % p
	B = mod_exp(g,b,p)#(g**b) % p
	global server_s
	server_s = mod_exp(A,b,p)
	#print("server_s",server_s)
	return B

def response_server(enc_message,IV):
	key = sha1.sha1(server_s.to_bytes(256,byteorder='big'))[:16]
	#print("server's key=",key)
	message = set_2.aes_cbc_mode_dec(enc_message,IV,key)
	print("server thinks A's message=",message)
	message = b"I ain't the sharpest tool in the shed" #I just realized I wasn't padding before blockifying in my set_2 code...
	#print("server's message",message)
	return set_2.aes_cbc_mode_enc(message,IV,key)

def standard_client():
	print("-"*10+"starting standard client interaction"+"-"*10)
	p = big_p
	g = 2
	a = random.randint(0,p) % p
	A = mod_exp(g,a,p)#(g**a) % p
	B = diffie_server(p,g,A)
	client_s = mod_exp(B,a,p)
	#print("client_s",client_s)
	message = b"Somebody once told me the world is gonna roll me"
	key = sha1.sha1(client_s.to_bytes(256,byteorder='big'))[:16]
	#print("client's key=",key)
	IV = urandom(16)
	server_response = response_server(set_2.aes_cbc_mode_enc(message,IV,key),IV)
	server_message = set_2.aes_cbc_mode_dec(server_response,IV,key)
	print("client recieved",server_message)
	print("-"*10+"end of standard client interaction"+"-"*10)


def middle_one(p,g,A):
	print("MITM says hi!")
	#Client is expecting B, server is expecting p,g,A
	fake_B = diffie_server(p,g,p)
	#server_s = (p**b) mod p = 0
	#client_s is also = 0
	return p

def middle_two(enc_message,IV):
	print("MITM says hi!")
	key = sha1.sha1(bytes(256))[:16] #just sha-1 of \x00 bytes
	stolen_message = set_2.aes_cbc_mode_dec(enc_message,IV,key)
	print("man in the middle found, ",stolen_message)
	server_response = response_server(set_2.aes_cbc_mode_enc(stolen_message,IV,key),IV)
	stolen_message = set_2.aes_cbc_mode_dec(server_response,IV,key)
	print("man in the middle found, ",stolen_message)
	return server_response

def innocent_bystander():
	print("-"*10+"starting man in the middle interaction"+"-"*10)
	p = big_p
	g = 2
	a = random.randint(0,p) % p
	A = mod_exp(g,a,p)#(g**a) % p
	B = middle_one(p,g,A)

	client_s = mod_exp(B,a,p)
	#print("client_s",client_s)
	message = b"Somebody once told me the world is gonna roll me"
	key = sha1.sha1(client_s.to_bytes(256,byteorder='big'))[:16]
	#print("client's key=",key)
	IV = urandom(16)
	server_response = middle_two(set_2.aes_cbc_mode_enc(message,IV,key),IV)
	server_message = set_2.aes_cbc_mode_dec(server_response,IV,key)
	print("client recieved",server_message)
	print("-"*10+"end of man in the middle interaction"+"-"*10)


server_s = 0
server_p = 0
server_g = 0
server_B = 0
def diffie_server_v2(p,g,msg_type,A):
	if msg_type:
		global server_p, server_g
		server_p = p
		server_g = g
		return True
	else:
		global server_B, server_s
		b = random.randint(0,server_p) % server_p
		server_B = mod_exp(server_g,b,server_p)
		server_s = mod_exp(A,b,server_p)
		return server_B

def standard_client_v2():
	print("-"*10+"starting standard client_v2 interaction"+"-"*10)
	p = big_p
	g = 2
	resp = diffie_server_v2(p,g,True,0)
	assert(resp)

	a = random.randint(0,p) % p
	A = mod_exp(g,a,p)#(g**a) % p
	B = diffie_server_v2(0,0,False,A)
	client_s = mod_exp(B,a,p)
	#print("client_s",client_s)
	message = b"Somebody once told me the world is gonna roll me"
	key = sha1.sha1(client_s.to_bytes(256,byteorder='big'))[:16]
	#print("client's key=",key)
	IV = urandom(16)
	server_response = response_server(set_2.aes_cbc_mode_enc(message,IV,key),IV)
	server_message = set_2.aes_cbc_mode_dec(server_response,IV,key)
	print("client recieved",server_message)
	print("-"*10+"end of standard client_v2 interaction"+"-"*10)

fake_g = 1
intercepted_p = 0
def man_in_the_middle_v2(p,g,msg_type,A):
	print("MITM says hi!")
	if msg_type:
		global intercepted_p
		global fake_g 
		#fake_g = 1
		#fake_g = p
		fake_g = p-1
		intercepted_p = p
		return diffie_server_v2(p,fake_g,msg_type,A)
	else:
		#Client is expecting B back
		#Server is expecting to get A so let's just send it over A=1 so it's secret is always 1
		return diffie_server_v2(p,g,msg_type,1)

def middle_reader_v2(enc_message,IV):
	print("MITM says hi!")
	if fake_g == 1:
		#then we know that the B that the server generated is 1, so client_s = (B**a) mod p = 1
		client_key = 1
		client_key = sha1.sha1(client_key.to_bytes(256,byteorder='big'))[:16]
		#The server's secret is just (A**b) mod p, which is 1 because we faked A=1
		server_key = 1
		server_key = sha1.sha1(server_key.to_bytes(256,byteorder='big'))[:16]

	elif fake_g == intercepted_p:
		#Server's B is going to be (p**b) mod p, which is always 0, client_s is going to be 0
		client_key = 0
		client_key = sha1.sha1(client_key.to_bytes(256,byteorder='big'))[:16]

		#The server's secret is just (A**b) mod p, which is 1 because we faked A=1
		server_key = 1
		server_key = sha1.sha1(server_key.to_bytes(256,byteorder='big'))[:16]
	elif fake_g == intercepted_p-1:
		#server_B = ((p-1)**b) mod p = (-1)**b, so either +1 or -1, we can just try both
		#client_s = (server_B ** a) mod p = +1 or -1
		client_key_1 = 1
		client_key_1 = sha1.sha1(client_key_1.to_bytes(256,byteorder='big'))[:16]

		client_key_2 = -1
		client_key_2 = sha1.sha1(client_key_2.to_bytes(256,byteorder='big',signed=True))[:16]

		possible_1 = set_2.aes_cbc_mode_dec(enc_message,IV,client_key_1)
		possible_2 = set_2.aes_cbc_mode_dec(enc_message,IV,client_key_2)
		score_1 = set_1.get_score(possible_1)
		score_2 = set_1.get_score(possible_2)

		if score_1 > score_2:
			client_key = client_key_1
		else:
			client_key = client_key_2

		#The server's secret is just (A**b) mod p, which is 1 because we faked A=1
		server_key = 1
		server_key = sha1.sha1(server_key.to_bytes(256,byteorder='big'))[:16]

	stolen_message = set_2.aes_cbc_mode_dec(enc_message,IV,client_key)
	print("man in the middle found, ",stolen_message)
	server_response = response_server(set_2.aes_cbc_mode_enc(stolen_message,IV,server_key),IV)
	stolen_message = set_2.aes_cbc_mode_dec(server_response,IV,server_key)
	print("man in the middle found, ",stolen_message)
	return set_2.aes_cbc_mode_enc(stolen_message,IV,client_key)

def naive_bystander():
	print("-"*10+"starting naive_bystander interaction"+"-"*10)
	p = big_p
	g = 2
	resp = man_in_the_middle_v2(p,g,True,0)
	assert(resp)

	a = random.randint(0,p) % p
	A = mod_exp(g,a,p)#(g**a) % p
	B = man_in_the_middle_v2(0,0,False,A)
	client_s = mod_exp(B,a,p)
	#print("client_s",client_s)
	message = b"Somebody once told me the world is gonna roll me"
	key = sha1.sha1(client_s.to_bytes(256,byteorder='big'))[:16]
	#print("client's key=",key)
	IV = urandom(16)
	server_response = middle_reader_v2(set_2.aes_cbc_mode_enc(message,IV,key),IV)
	server_message = set_2.aes_cbc_mode_dec(server_response,IV,key)
	print("client recieved",server_message)
	print("-"*10+"end of naive_bystander interaction"+"-"*10)

def sha256_HMAC(message,key):
	block_size = 64
	output_size = 20

	if len(key) > block_size:
		m0 = hashlib.sha256()
		m0.update(key)
		key = m0.digest()

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

	m = hashlib.sha256()
	m.update(i_key_pad)
	m.update(message)
	res1 = m.digest()

	m1 = hashlib.sha256()
	m1.update(o_key_pad)
	m1.update(res1)
	return m1.digest()
	#return codecs.decode(sha1.sha1(o_key_pad + codecs.decode(sha1.sha1(i_key_pad + message),'hex')),'hex')

N = big_p
g = 2
k = 3
I = "dankmemes@nowhere.com"
v = 0
salt = 0
server_u = 0

def srp_server_init():
	P = "hunter2"
	global v, salt
	salt = random.randint(0,2**32-1)
	m = hashlib.sha256()
	m.update(salt.to_bytes(32,byteorder='big'))
	m.update(P.encode('ascii'))
	xH = m.digest()
	x = int.from_bytes(xH,byteorder='big')
	v = mod_exp(g,x,N)

def srp_server(A,I):
	global server_u
	b = random.randint(0,N)
	B = k*v + mod_exp(g,b,N)
	m = hashlib.sha256()
	m.update(A.to_bytes(256,byteorder='big'))
	m.update(B.to_bytes(256,byteorder='big'))
	uH = m.digest()
	server_u = int.from_bytes(uH,byteorder='big')

	S = mod_exp((A * mod_exp(v,server_u,N)),b,N)

	m2 = hashlib.sha256()
	m2.update(S.to_bytes(256,byteorder='big'))
	K = m2.digest()
	#print(K)
	to_confirm_against = sha256_HMAC(K,salt.to_bytes(32,byteorder='little'))
	print("server's HMAC=",to_confirm_against)
	return salt,B

def srp_client():
	print("hi server i wanna start")
	P = "hunter2"
	srp_server_init()

	a = random.randint(0,N)
	A = mod_exp(g,a,N)
	salt,B = srp_server(A,I)

	m = hashlib.sha256()
	m.update(A.to_bytes(256,byteorder='big'))
	m.update(B.to_bytes(256,byteorder='big'))
	uH = m.digest()
	client_u = int.from_bytes(uH,byteorder='big')

	assert(client_u == server_u)

	#print("making x")
	m2 = hashlib.sha256()
	m2.update(salt.to_bytes(32,byteorder='big'))
	m2.update(P.encode('ascii'))
	xH = m2.digest()
	x = int.from_bytes(xH,byteorder='big')

	#print("making K")
	S = mod_exp((B- k*mod_exp(g,x,N)),(a + client_u * x),N)
	m3 = hashlib.sha256()
	m3.update(S.to_bytes(256,byteorder='big'))
	K = m3.digest()
	#print(K)

	to_send = sha256_HMAC(K,salt.to_bytes(32,byteorder='little'))
	print("HMAC to test",to_send)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def srp_client_sockets():
	print("hi server i wanna start")
	P = "hunter2"
	sock.connect(("", 1337))
	util = sock_util.Util(sock)

	a = random.randint(0,N)
	A = mod_exp(g,a,N)

	util.writenum(A)
	util.writeline(I.encode('ascii'))

	#salt,B = srp_server(A,I,0)
	salt = util.readnum()
	B = util.readnum()

	m = hashlib.sha256()
	m.update(A.to_bytes(256,byteorder='big'))
	m.update(B.to_bytes(256,byteorder='big'))
	uH = m.digest()
	client_u = int.from_bytes(uH,byteorder='big')

	#assert(client_u == server_u)

	#print("making x")
	m2 = hashlib.sha256()
	m2.update(salt.to_bytes(32,byteorder='big'))
	m2.update(P.encode('ascii'))
	xH = m2.digest()
	x = int.from_bytes(xH,byteorder='big')

	#print("making K")
	S = mod_exp((B- k*mod_exp(g,x,N)),(a + client_u * x),N)
	m3 = hashlib.sha256()
	m3.update(S.to_bytes(256,byteorder='big'))
	K = m3.digest()
	#print(K)

	to_send = sha256_HMAC(K,salt.to_bytes(32,byteorder='little'))
	print("HMAC to test",to_send)

	util.writebytes(to_send)
	res = util.readline()
	#print("login result:",res)
	if res == b"success":
		print("login successful")
	else:
		print("login failed")

def challenge_37():
	global sock
	print("hi server i wanna start")
	sock.connect(("", 1337))
	util = sock_util.Util(sock)

	A = 0 #N #2N all work
	util.writenum(A)
	util.writeline(I.encode('ascii'))

	#salt,B = srp_server(A,I,0)
	salt = util.readnum()
	_ = util.readnum()

	S = 0 #lmao r e k t
	m3 = hashlib.sha256()
	m3.update(S.to_bytes(256,byteorder='big'))
	K = m3.digest()
	#print(K)

	to_send = sha256_HMAC(K,salt.to_bytes(32,byteorder='little'))
	print("HMAC to test",to_send)

	util.writebytes(to_send)
	res = util.readline()
	#print("login result:",res)
	if res == b"success":
		print("A = 0 or N or 2*N, S = 0 ezpz")
	else:
		print("login failed")

email = "maowmaowmaowmaow@gmail.com"
passwd = "awesome"
server_salt = 0
server_v = 0
N = big_p
g = 2
server_HMAC = 0

attacker_B = 0
attacker_A = 0
def middle_init():
	global server_salt, server_v
	server_salt = random.randint(0,2**32-1)
	m = hashlib.sha256()
	m.update(server_salt.to_bytes(32,byteorder='big'))
	m.update(passwd.encode('ascii'))
	x = int.from_bytes(m.digest(), byteorder='big')
	server_v = pow(g,x,N)

def middle_two(A):
	#b = random.randint(0,N)
	b = 1
	B = pow(g,b,N)
	u = 1
	#u = random.randint(0,2**128)

	#print("A=",A,"v=",server_v,"u=",u,"b=",b,N)
	server_S = pow(A*pow(server_v,u,N),b,N)
	#print("server_S=",server_S)
	m = hashlib.sha256()
	m.update(server_S.to_bytes(256,byteorder='big'))
	server_K = m.digest()

	global server_HMAC
	server_HMAC = sha256_HMAC(server_K,server_salt.to_bytes(32, byteorder='big'))

	global attacker_A, attacker_B
	attacker_B = B
	attacker_A = A
	return server_salt,B,u

def middle_attack(client_HMAC):
	#c_HMAC = sha256_HMAC(client_K, salt)
	#client_K = sha256(client_S)
	#client_S = B^(a+u*x) mod N
	#We can control everything in client_S but x, which is sha256(salt+passwd)

	#So we want to be able to recover the password? Without brute force?

	#JK it says dictionary attack
	words = open('/usr/share/dict/words').readlines()
	l = words[0][0]
	for w in words:
		w = w.strip().lower()
		if w[0] != l:
			l = w[0]
			print("cur letter=",l)
		m = hashlib.sha256()
		m.update(server_salt.to_bytes(32,byteorder='big'))
		#print("testing pass=",w)
		try:
			m.update(w.encode('ascii'))
			x = int.from_bytes(m.digest(),byteorder='big')
			v= pow(g,x,N)
			test_S = pow(attacker_A*pow(v,1,N),1,N)
			m = hashlib.sha256()
			m.update(test_S.to_bytes(256,byteorder='big'))
			test_K = m.digest()
			test_HMAC = sha256_HMAC(test_K,server_salt.to_bytes(32, byteorder='big'))
			if test_HMAC == client_HMAC:
				print("password=",w)
				break
		except UnicodeEncodeError:
			#print("stupid word")
			pass
	# if client_HMAC == server_HMAC:
	# 	print("yeet")
	# else:
	# 	print("neet")
def simplified_srp_client():
	middle_init()
	a = random.randint(0,N)
	A = pow(g,a,N)

	salt,B,u = middle_two(A)

	m = hashlib.sha256()
	m.update(server_salt.to_bytes(32,byteorder='big'))
	m.update(passwd.encode('ascii'))
	x = int.from_bytes(m.digest(), byteorder='big')

	client_S = pow(B,a+u*x,N)
	#print("client_S=",client_S)
	m = hashlib.sha256()
	m.update(client_S.to_bytes(256,byteorder='big'))
	client_K = m.digest()

	client_HMAC  = sha256_HMAC(client_K,salt.to_bytes(32, byteorder='big'))
	middle_attack(client_HMAC)

def challenges():
	#Challenge 33
	#s = diffie_hellman()
	# print(s)

	#Challenge 34
	#standard_client()
	#innocent_bystander()

	#Challenge 35
	#standard_client_v2()
	#naive_bystander()

	#Challenge 36
	#srp_client()
	#srp_client_sockets() #remember to open the server

	#Challenge 37
	#challenge_37() #remember to open the server

	#Challenge 38
	simplified_srp_client()
#After way too many challenges I'm setting this up
if __name__ == '__main__':
	challenges()