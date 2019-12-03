#!/usr/bin/env python3

import rabin
import os
import socketserver


class MyTCPHandler(socketserver.StreamRequestHandler):
    with open("flag1.txt", "rb") as f:
        flag1 = f.read().rstrip()
    with open("flag2.txt", "rb") as f:
        flag2 = f.read().decode().rstrip()

    private_key = rabin.keygen(1024)
    public_key = private_key.public_key()

    def handle(self):
        input, output = self.rfile, self.wfile
        flag1_message = self.flag1
        target_ciphertext = self.public_key.encrypt(flag1_message)

        try:
            output.write(f"o hai! my public key is:\n\n{self.public_key.n}\n\n".encode())
            output.write("which game do you want to play?\n\n".encode())
            output.write("1. decrypt a message\n".encode())
            output.write("2. factor the modulus\n\n".encode())

            while True:
                output.write("choice? ".encode())
                data = input.readline().decode().strip()
                if data in ["1", "2"]:
                    break
                else:
                    output.write("invalid choice!\n\n".encode())

            if data == "1":
                output.write(f"\nok, here's a ciphertext:\n\n{target_ciphertext}\n\n".encode())
                output.write("can you decrypt it?\n\n".encode())
                output.write("i'll let you decrypt almost anything you like.\n\n".encode())

                while True:
                    output.write("ciphertext? ".encode())
                    data = input.readline().decode().strip()

                    try:
                        ciphertext = int(data)
                    except ValueError:
                        output.write("invalid integer input!\n\n".encode())
                        continue

                    if ciphertext < 0:
                        output.write("too small!\n\n".encode())
                        continue

                    if ciphertext >= self.public_key.n:
                        output.write("too big!\n\n".encode())
                        continue

                    if ciphertext == target_ciphertext:
                        output.write("nice try!\n\n".encode())
                        continue

                    plaintext = self.private_key.decrypt(ciphertext)
                    if plaintext:
                        output.write(f"the plaintext is: {plaintext.hex()}\n\n".encode())
                    else:
                        output.write("plaintext didn't have correct redundancy!\n\n".encode())
            elif data == "2":
                output.write("all right, give me p or q!\n\n".encode())

                while True:
                    output.write("input? ".encode())
                    data = input.readline().decode().strip()

                    try:
                        factor = int(data)
                    except ValueError:
                        output.write("invalid integer input!\n\n".encode())
                        continue

                    if factor in [self.private_key.p, self.private_key.q]:
                        output.write(f"you got it! here's your flag: {self.flag2}\n".encode())
                        break
                    else:
                        output.write("nope!\n\n".encode())


        except (BrokenPipeError, ConnectionResetError):
            pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 7979

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
