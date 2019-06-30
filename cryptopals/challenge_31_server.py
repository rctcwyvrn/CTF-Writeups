#Seperate one because I don't know how to web, code taken from https://github.com/akalin/cryptopals-python3/blob/master/challenge31.py and https://github.com/akalin/cryptopals-python3/blob/master/challenge31_server.py
from os import urandom
import codecs, set_1
#import set_4
import sha1
import http.server
import socketserver
import time
import urllib.parse

HMAC_key = urandom(16)
PORT = 9000
DELAY = 0.005 #0.02 #0.05
last_file = b''

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

def insecure_compare(digest,signature):
    if len(digest) != len(signature):
        print("too short", len(digest), len(signature))
        return False

    for x,y in zip(digest,signature):
        if x !=y:
         return False

        time.sleep(DELAY)

    return True

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global last_file
        result = urllib.parse.urlparse(self.path)
        print(result)
        if result.path == '/test':
            q = urllib.parse.parse_qs(result.query) #parse the url
            file = q['file'][0].encode('ascii') #Get the file part
            print("File=",file)
            digest = sha1_HMAC(file, HMAC_key) #digest the file
            signature = codecs.decode((q['signature'][0]),'hex') #get the signature
            # if file != last_file:
            #     last_file = file
            #     print('New file:', file, codecs.encode(digest,'hex'))
            print("Correct = ",codecs.encode(digest,'hex'), "Given =",codecs.encode(signature,'hex'))
            if insecure_compare(digest, signature):
                self.send_error(200)
            else:
                self.send_error(500)
        else:
            self.send_error(500)

def main(delay):
    global DELAY
    DELAY = delay
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), RequestHandler)
    print("serving at port {0} with delay {1}".format(PORT, DELAY))
    httpd.serve_forever()

if __name__ == '__main__':
	main(DELAY)