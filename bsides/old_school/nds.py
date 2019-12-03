#!/usr/bin/env python3

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
    highbits = 0
    for x in range(8):
        highbits |= (input[x] & 0x80) >> x
    t = key[highbits]

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
