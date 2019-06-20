
thing = ')\x06\x16O+50\x1eQ\x1b[\x14K\x08]+R\x17\x01W\x16\x11\\\x07]'
message = "You have now entered the Duck Web, and you're in for a honkin' good time.\nCan you figure out my trick?"

out = ""
for i in range(25):
	a = ord(thing[i])
	b = ord(message[i])
	res = a ^ b
	char = chr(res)
	out +=char

print(out)


#main prints out you're a winner if you input the flag, so basically a string st message[i] = in[i] xor thing[i]
#xor can be reversed, because if m[i] = 1 then in[i] = 1 or thing[i] =1. If thing[i] =1 then in[i] = 0, otherwise in[i] = 1
#so it turns out that in = thing xor message
# A XOR B = C implies B XOR C = A