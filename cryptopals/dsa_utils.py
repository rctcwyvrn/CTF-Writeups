import random, hashlib
from Crypto.Util import number
from decimal import *

p = int("""800000000000000089e1855218a0e7dac38136ffafa72eda7859f2171e25e65eac698c1702578b07dc2a1076da241c76c62d374d8389ea5aeffd3226a0530cc565f3bf6b50929139ebeac04f48c3c84afb796d61e5a4f9a8fda812ab59494232c7d2b4deb50aa18ee9e132bfa85ac4374d7f9091abc3d015efc871a584471bb1""",16)
q = int("f4f47f05794b256174bba6e9b396a7707e563c5b",16)
g = int("""5958c9d3898b224b12672c0b98e06c60df923cb8bc999d119458fef538b8fa4046c8db53039db620c094c9fa077ef389b5322a559946a71903f990f1f7e0e025e2d7f7cf494aff1a0470f5b64c36b625a097f1651fe775323556fe00b3608c887892878480e99041be601a62166ca6894bdd41a7054ec89f756ba9fc95302291""",16)

class dsa:
     def __init__(self):
          #self.x = q // 3
          self.x = random.randint(1,q-1)
          self.y = pow(g,self.x,p)
          #print("myprivkey is ",self.x)

     def pubkey(self):
          return self.y

     def sign(self,msg):
          r,s,k = self.sign_oops(msg) #lmao i just don't wanna have that massive block of copy pasted code. this is dumb
          return r,s

     def sign_oops(self,msg):
          hash_int = self.H(msg)

          r = 0
          s = 0
          while s == 0:
               while r == 0:
                    k = random.randint(1,q-1)

                    #k = q // 2
                    r = pow(g,k,p) % q
               s = (number.inverse(k,q) * (hash_int + self.x * r )) % q # requires privkey x

          return (r,s,k)


     def H(self,msg):
          H = hashlib.sha256()
          H.update(msg)
          hashed_msg = H.digest()
          hash_int = number.bytes_to_long(hashed_msg)
          return hash_int

     def verify(self,sig,msg):
          hash_int = self.H(msg)

          r,s = sig

          if not ((0 < r < q) and (0 < s < q)):
               print("wtf did you send me")
               return False

          w = number.inverse(s,q)
          u1 = (hash_int * w) % q
          u2 = (r * w) % q

          t1 = pow(g,u1,p)
          t2 = pow(self.y,u2,p) #only needs pubkey y

          v = ((t1 * t2) % p ) % q
          #v = ((pow(g,u1,p) * pow(self.y,u2,p)) % p) % q
          #v = ((g ** u1 * self.y ** u2) % p )% q
          if v == r:
               print("signature accepted")
               return True
          else:
               print("failed, {} vs {}".format(v,s))

               return False


if __name__ == "__main__":
     d = dsa()
     msg = b'MAOWMAOWMAOWMAOW'
     sig = d.sign(msg)
     print("r={}, s={}".format(sig[0],sig[1]))

     d.verify(sig,msg)

               

