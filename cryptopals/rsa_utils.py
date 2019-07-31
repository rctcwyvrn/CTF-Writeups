from Crypto.Util import number
import codecs
import binascii


def rsa_crypt(key,val,n):
	return pow(val,key,n)

class rsa:
	def __init__(self,e=3):
		good = False
		while not good:
			#p = number.getPrime(128)
			#q = number.getPrime(128)
			#p = number.getStrongPrime(640)
			#q = number.getStrongPrime(640)
			p = number.getStrongPrime(1024)
			q = number.getStrongPrime(1024)

			n = p * q

			toit = (p-1) * (q-1)
			if toit % e == 0:
				good = False
			else:
				good = True

		d = number.inverse(e,toit)
		print("keys generated")
		
		self.pub = e
		self.priv = d
		self.n = n

	def enc(self,m):
		if isinstance(m,str):
			m = codecs.encode(m,'utf-8')
			#print("before",m)
			m = number.bytes_to_long(m)

		return pow(m, self.pub, self.n)

	def dec(self,m):
		val = pow(m, self.priv, self.n)
		v = number.long_to_bytes(val)
		#print("after",v)
		return v.decode("utf-8")

	def pubkey(self):
		return (self.pub,self.n)

