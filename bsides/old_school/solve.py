#!/usr/bin/env python3

import os
# S-boxes
S0 = [1, 8, 12, 10, 4, 3, 13, 5, 14, 0, 2, 6, 15, 9, 7, 11]
S1 = [15, 9, 8, 14, 2, 7, 6, 13, 4, 10, 11, 12, 0, 3, 1, 5]

# permutation (P-box)
P = []
for byte in range(8):
    for bit in range(8):
        P.append(bit * 8 + byte)


def f(input, key):
    """the Feistel round function"""
    print(input)
    highbits = 0
    for x in range(8):
        highbits |= (input[x] & 0x80) >> x
    print("high",highbits)
    t = key[highbits]
    #print("t",t)

    #t = 20

    p = 0
    for x in range(8):
        bit = (t >> x) & 1
        p <<= 8
        if bit:
            p |= (S1[input[x] & 0xf] << 4) | S0[input[x] >> 4]
        else:
            p |= (S0[input[x] >> 4] << 4) | S1[input[x] & 0xf]

    output = 0
    for x in range(64):
        output |= ((p >> x) & 1) << P[x]
    return output.to_bytes(8, byteorder="big")


def cipher_block(input, key):
    """encrypt or decrypt a single block"""
    for x in range(16):
        input = input[8:16] + bytes([a ^ b for a, b in zip(input[0:8], f(input[8:16], key))])
    return input[8:16] + input[0:8]


def cipher(input, key):
    """encrypt or decrypt multiple blocks in ECB mode"""
    output = b""
    for x in range(0, len(input), 16):
        output += cipher_block(input[x:x+16], key)
    return output

key = [20, 137, 15, 80, 180, 141, 169, 182, 32, 109, 235, 160, 38, 240, 124, 107, 131, 142, 101, 43, 214, 70, 244, 178, 69, 38, 25, 45, 206, 44, 133, 148, 116, 217, 143, 163, 225, 54, 10, 196, 156, 41, 71, 165, 212, 189, 45, 209, 250, 123, 38, 179, 122, 30, 239, 95, 103, 180, 207, 117, 240, 104, 140, 169, 244, 189, 41, 50, 240, 85, 20, 189, 82, 16, 141, 183, 234, 66, 216, 91, 160, 151, 138, 49, 54, 127, 173, 26, 126, 29, 143, 27, 135, 116, 63, 211, 55, 20, 58, 38, 187, 207, 91, 205, 196, 213, 125, 57, 214, 36, 138, 226, 86, 12, 188, 71, 152, 120, 103, 196, 126, 22, 59, 203, 7, 201, 112, 164, 51, 5, 185, 58, 157, 21, 77, 108, 215, 78, 87, 126, 151, 197, 94, 234, 215, 124, 142, 163, 130, 150, 172, 153, 140, 231, 231, 116, 48, 114, 72, 120, 243, 9, 240, 104, 123, 83, 194, 126, 103, 30, 244, 180, 118, 90, 57, 137, 176, 38, 207, 23, 203, 138, 7, 121, 178, 141, 198, 46, 200, 172, 16, 178, 36, 20, 217, 165, 99, 0, 121, 25, 151, 230, 105, 109, 112, 26, 127, 180, 58, 130, 14, 91, 78, 239, 112, 0, 132, 172, 191, 252, 187, 177, 71, 52, 103, 142, 210, 177, 25, 237, 80, 1, 233, 74, 129, 211, 220, 74, 107, 78, 178, 16, 171, 124, 101, 31, 140, 248, 226, 15, 12, 40, 171, 89, 35, 174]


#flag = bytes.fromhex("ff"*16)
#print(f(flag[:16],key))

flag = bytes.fromhex("f8702259319adc71bc4ab6efb6230c5f6cd18dcded09a83dc92ff8dd1901db7f")
print(cipher(flag,key))


