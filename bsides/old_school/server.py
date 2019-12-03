#!/usr/bin/env python3

import nds
import os
import socketserver

welcome_message = """AES is barely two decades old. Not nearly enough to be trusted yet.
So we're going with a cipher that's been around since the 1970's.
It's the only way to be sure our most valuable secret will stay safe:"""


class MyTCPHandler(socketserver.StreamRequestHandler):
    with open("flag.txt", "rb") as f:
        flag = f.read(32) #flag is 2 blocks long

    key = os.urandom(256)

    def handle(self):
        input, output = self.rfile, self.wfile
        flag_encrypted = nds.cipher(self.flag, self.key)

        try:
            output.write(welcome_message.encode())
            output.write(("\n\n" + flag_encrypted.hex() + "\n").encode())

            while True:
                output.write("\nPlaintext or ciphertext input? ".encode())
                data = input.readline().decode().strip()

                try:
                    data_bytes = bytes.fromhex(data)
                except ValueError:
                    output.write("Invalid hex input.\n".encode())
                    continue

                if len(data_bytes) % 16 != 0:
                    output.write("Input must be a multiple of 16 bytes.\n".encode())
                    continue

                bad = False
                for x in range(0, len(data_bytes), 16):
                    if data_bytes[x:x+16] in [flag_encrypted[0:16], flag_encrypted[16:32]]: # checks if any of the data blocks are one of the two flag blocks
                        output.write("Not so fast! You're not allowed to decrypt that!\n".encode())
                        bad = True
                        break
                if bad:
                    continue

                output.write((nds.cipher(data_bytes, self.key).hex() + "\n").encode())

        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
