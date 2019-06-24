#!/bin/sh

echo $1 > /tmp/plain.key; xxd -r -p /tmp/plain.key > /tmp/enc.key
echo "U2FsdGVkX18+Wl0awCH/gWgLGZC4NiCkrlpesuuX8E70tX8t/TAarSEHTnpY/C1D" | openssl enc -d -aes-256-cbc -pbkdf2 -md sha1 -base64 --pass file:/tmp/enc.key > std_out.txt 2> std_err.txt