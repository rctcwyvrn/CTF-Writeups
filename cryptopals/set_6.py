import rsa_utils as rsa
from Crypto.Util import number
import set_5
import binascii, hashlib
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
	#print("without padding",stuff)
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
		#print("trying to find a nice cube")

		fake_sig = set_5.cube_root(number.bytes_to_long(fake))
		t = int(fake_sig)
		diff = t**3 - number.bytes_to_long(fake)
		#print("difference", diff)
		#print("space=",space)
		#print("diff in bytes = ", len(number.long_to_bytes(diff)))
		len_diff = len(number.long_to_bytes(diff))

		buffer_size+=16
	print("signature has been forged, will decrypt to = {}".format(fake))
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


	#Goal
	#b'\x08H4\xe7R\xd6\x8d@z\xcb\xd3\xb2\xd4\xb2&\xd1\xdc\xbf\x1c\x82\xa0\x06\x1a\x8dl\x81\xd8\x9d\x17\xa9\xb2\xc0'
	#b'\x08H4\xe7R\xd6\x8d@z\xcb\xd3\xb2\xd54\xf9\x93K\x1d\xdc\x17\x00\xb2\xd8\n\xd3\x05\xcejq\xb6o\xf9'
	#b'\x08H4\xe7R\xd6\x8d@z\xcb\xd3\xb2\xd4\xb2&\xd1\xdc\xbf\x1c\x82\xa0\x06\x1a\x901\xa7\xa9\x14\x14hI\xb8'

	#gets messed up a bit because there isnt enogh garbagio and it ends up messing things up while trying to make a perfect cube
	#b'\x08H4\xe7R\xd6\x8d@z\xcb\xd3\xb2\xd54\xf9\x93K\x1d\xdc\x17\x00\xb2\xd8\n\xd3\x05\xcejq\xb6o\xf9' 
	#b'\x08H4\xe7R\xd6\x8d@z\xcb\xd3\xb2\xd4\xb2&\xd1\xdc\xbf,\xdfK.\x0b\x8e\x0f\x04\xde\xfb\xf9\x17\x90\x92'
	#b'\x08H4\xe7R\xd6\x8d@z\xcb\xd3\xb2\xd4\xb2&\xd1\xdc\xbf\x1c\x82\xa0\x06\x1a\x901\xa7\xa9\x14\x14hI\xb8'
	#b'\x08H4\xe7R\xd6\x8d@z\xcb\xd3\xb2\xd4\xb2&\xd1\xdc\xbf\x1c\x82\xa0\x06\x1a\x8dl\x81\xd8\x9d\x17\xa9\xb2\xc0' #with a total messagelen of 128
	#Runs pretty quick too, just 31 seconds
	#Nevermind its just cube
	

def challenges():
	global r
	r = rsa.rsa(3)


	#Challenge 41
	#challenge41()

	#Challenge 42
	challenge42()

if __name__ == "__main__":
	challenges()