import socketserver, sock_util
import sys, random

big_p = "ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff"
big_p = int(big_p,16)
N = big_p
g = 2
k = 3
I = "dankmemes@nowhere.com"
P = "hunter2"
v = 0
salt = 0
server_u = 0
server_hmac = 0

def srp_server_init():
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
    server_hmac = sha256_HMAC(K,salt.to_bytes(32,byteorder='little'))
    print("server's HMAC=",server_hmac)
    return salt,B

def readline(s):
    return s._rfile.readline().strip()

class SRPTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        util = sock_util.Util(self)
        srp_server_init()

        print('S: reading A and I')
        A = util.readline()
        I = util.readline()
        salt,B = srp_server(A,I)

        print('S: writing salt and B')
        util.writenum(salt)
        util.writenum(B)

        print("S: reading HMAC")
        HMAC = util.readbytes()

        if HMAC == server_hmac:
            print("S: logging in")
        else:
            print("S: login failed")

if __name__ == "__main__": 
    port = 1337
    print('listening on ' + ':' + str(port))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("", port), SRPTCPHandler)

server.serve_forever()