import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import constant_time

#from Crypto.Util import number
import math

def _hash(message):
    return hashlib.sha256(message).digest()[0:2]
    #return hashlib.sha256(message).digest()[0:6]


def _pkcs1v15_pad(message, key_bytes):
    hashed_message = _hash(message)
    padding_len = key_bytes - len(hashed_message) - 3
    print("padding len=", padding_len)
    padding = bytes([0x00, 0x01] + [0xff] * padding_len + [0x00])
    print("pkcs padded msg=", padding + hashed_message)
    print("pkcs hashed message = ", hashed_message)
    return padding + hashed_message


def keygen(key_size):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return public_key, private_key


def sign(message, private_key):
    d = private_key.private_numbers().d
    n = private_key.public_key().public_numbers().n
    key_bytes = private_key.key_size // 8
    print("keybytes = ", key_bytes)
    padded_hash = _pkcs1v15_pad(message, key_bytes)
    print("lg of the padded msg = ",math.log(int.from_bytes(padded_hash, byteorder="big"),2))
    print("test = ", (n+1).to_bytes(key_bytes, byteorder='big'))
    return pow(int.from_bytes(padded_hash, byteorder="big"), d, n).to_bytes(key_bytes, byteorder="big")


def verify(message, signature, public_key):
    e = public_key.public_numbers().e
    n = public_key.public_numbers().n
    key_bytes = public_key.key_size // 8

    print("keybytes = ", key_bytes)

    padded_hash = pow(int.from_bytes(signature, byteorder="big"), e, n)
    print("padded hash = ", padded_hash)

    #print("using Crypto", number.long_to_bytes(padded_hash))

    padded_hash = padded_hash.to_bytes(key_bytes, byteorder="big")
    print("padded hash truncated?= ", padded_hash)

    expected_padded_hash = _pkcs1v15_pad(message, key_bytes)
    print("expected signature = ", expected_padded_hash)
    return constant_time.bytes_eq(padded_hash, expected_padded_hash)


# message = b'ice ice baby'
# pub_key, priv_key = keygen(1024)

# signed = sign(message, priv_key)
# print("signature=",signed)
# print(verify(message,signed,pub_key))
# print(verify(message,b'\x00',pub_key))