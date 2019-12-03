import rsa

sig = "0c52d6c405f8786251832ece8a9b547930351ad572a5ec011937c54199a93ecebaa54cf812fc804490036101a588ab557f0eca0fe5c516c2e9660e939753e1c7690672ee79d09c2778dd9fa028c856f4123f89556a82887b3a9cb6c6abe1d27e2b12032ebce6689ce9a488bf79a230e1538d9ec397fbd58af095247b7b9cba32"
msg = "convert womancat.jpg \( -pointsize 40 -size 504x -gravity Center caption:abqm caption:abqm +append \) -gravity Center -append png:-"

padded_msg = rsa._pkcs1v15_pad(msg.encode(),128)
p_msg_int = int.from_bytes(padded_msg, byteorder="big")
print(p_msg_int)