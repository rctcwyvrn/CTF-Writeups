#https://github.com/akalin/cryptopals-python3 sauce

import hashlib
import socket
import socketserver, base64
#import util

class Util:
    def __init__(self, o):
        if isinstance(o, socket.socket):
            f = o.makefile(mode='rwb', buffering=0)
            self._rfile = f
            self._wfile = f
        elif isinstance(o, socketserver.StreamRequestHandler):
            self._rfile = o.rfile
            self._wfile = o.wfile
        else:
            raise Exception('unexpected')

    def readline(self):
        return self._rfile.readline().strip()

    def readnum(self):
        return int(self.readline())

    def readbytes(self):
        return base64.b64decode(self.readline())

    def writeline(self, line):
        self._wfile.write(line + b'\n')

    def writenum(self, num):
        self.writeline(str(num).encode('ascii'))

    def writebytes(self, bytes):
        self.writeline(base64.b64encode(bytes))
